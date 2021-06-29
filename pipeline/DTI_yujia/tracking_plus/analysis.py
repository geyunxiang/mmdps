import numpy as np

from dipy.io.image import load_nifti_data, load_nifti
from dipy.tracking import metrics
from dipy.tracking import utils
from dipy.tracking.streamline import Streamlines
from dipy.io.streamline import load_trk, save_trk
from mmdps.util import dwi
from dipy.tracking.utils import unique_rows, length

import os
import json


from dipy.segment.bundles import RecoBundles
from dipy.align.streamlinear import whole_brain_slr

from dipy.io.stateful_tractogram import Space, StatefulTractogram
from dipy.io.utils import create_tractogram_header

import time

def reduct(streamlines, data):

    new_streamlines = []


    for i in range(len(streamlines)):


        line = streamlines[i]
        line = np.round(line).astype(np.intp)
        line = unique_rows(line)

        flag = 0

        if line.shape[0] > 1:

            for j in range(line.shape[0]):
                #print(line[j, :])
                if data[line[j, 0], line[j, 1], line[j, 2]].any() == 0:
                    flag = 1
                    break


            if flag == 0:
                new_streamlines.append(line)

    return new_streamlines


def cal_ROI_num(mask_path, track_path, normdata_path, name, method_index, atlas, index, output):


    if normdata_path == None:
        norm_file = os.path.join('./data/DWI', name, 'norm.nii.gz')
    else:
        norm_file = normdata_path
    data, affine = load_nifti(norm_file)

    if method_index == 1:
        method = 'EuDX'
    elif method_index == 2:
        method = 'probabilistic'
    elif method_index == 3:
        method = 'deterministic'
    elif method_index == 4:
        method = 'sfm'
    elif method_index == 5:
        method = 'pft'
    else:
        method = None


    if track_path == None:

        trackfile = os.path.join('./Result/Track', 'tractogram_'+method+'_'+name+'.trk')
    else:
        trackfile = os.path.join(track_path, 'tractogram_'+method+'_'+name+'.trk')
    tracks = dwi.load_streamlines_from_trk(trackfile)
    tracks = reduct(tracks)

    index = str(index)


    if mask_path == None:

        ROI_file = os.path.join('./data/atlas', atlas, 'ROI_'+index+'_2.nii.gz')
    else:
        ROI_file = mask_path


    ROI_mask = load_nifti_data(ROI_file)
    cc_slice = np.zeros(data.shape[:3])
    cc_slice[:ROI_mask.shape[0], :ROI_mask.shape[1], :ROI_mask.shape[2]] = ROI_mask

    cc_streamlines = utils.target(tracks, affine, cc_slice.astype(np.float))
    cc_streamlines = Streamlines(cc_streamlines)

    if not os.path.isfile(output):
        mode = 'w+'
    else:
        mode = 'r+'


    with open(output, mode) as fileR:  # 打开文本读取状态

        strF = fileR.read()
        #print(len(strF))
        if len(strF) == 0:
            R = {}

        else:

            R = json.loads(strF)  # 解析读到的文本内容 转为python数据 以一个变量接收

        #print(args.name in R.keys())

        if name in R.keys():
            a = R[name]
            a[index] = len(cc_streamlines)
            R[name] = a
        else:
            a = {index:len(cc_streamlines)}
            R[name] = a

    with open(output, 'w') as fileR:

        jsObj = json.dumps(R, indent=4)
        fileR.write(jsObj)


def path_length(streamlines=None, track_path=None):

    if streamlines != None:
        return list(length(streamlines))
    else:
        track = load_trk(track_path)
        return list(length(track))


def bundle_extract(atlas_track_path, atlas_bundle_path, target_track_path):

    time0 = time.time()

    atlas_file = atlas_track_path
    target_file = target_track_path

    print('loading data begin! time:', time.time()-time0)


    sft_atlas = load_trk(atlas_file, "same", bbox_valid_check=False)
    atlas = sft_atlas.streamlines
    atlas_header = create_tractogram_header(atlas_file,
                                            *sft_atlas.space_attributes)


    sft_target = load_trk(target_file, "same", bbox_valid_check=False)
    target = sft_target.streamlines
    target_header = create_tractogram_header(target_file,
                                             *sft_target.space_attributes)


    moved, transform, qb_centroids1, qb_centroids2 = whole_brain_slr(
        atlas, target, x0='affine', verbose=True, progressive=True,
        rng=np.random.RandomState(1984))

    bundle_track = StatefulTractogram(moved, target_header,
                                      Space.RASMM)
    save_trk(bundle_track, 'moved.trk', bbox_valid_check=False)



    np.save("slr_transform.npy", transform)



    model_bundle_file = atlas_bundle_path
    model_bundle = load_trk(model_bundle_file, "same", bbox_valid_check=False)
    model_bundle = model_bundle.streamlines

    print('comparing begin! time:', time.time() - time0)

    rb = RecoBundles(moved, verbose=True, rng=np.random.RandomState(2001))

    recognized_bundle, bundle_labels = rb.recognize(model_bundle=model_bundle,
                                                  model_clust_thr=0,
                                                  reduction_thr=20,
                                                  reduction_distance='mam',
                                                  slr=True,
                                                  slr_metric='asymmetric',
                                                  pruning_distance='mam')




    bundle_track = StatefulTractogram(target[bundle_labels], target_header,
                                    Space.RASMM)
    return bundle_track
    #save_trk(bundle_track, "CST_R.trk", bbox_valid_check=False)







