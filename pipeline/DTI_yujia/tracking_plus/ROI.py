from dipy.io.image import load_nifti_data, load_nifti
from dipy.io.streamline import load_trk
from dipy.tracking import metrics
from dipy.tracking import utils
from dipy.tracking.streamline import Streamlines
from mmdps.util import dwi
import nibabel as nib
import argparse
import os
import numpy as np
import json

def IsGrowFromROI(streamlines, ROI, one_node, two_node):

    top = (streamlines[0]).astype('int')
    bo = (streamlines[-1]).astype('int')

    #print(top)
    #print(bo)
    #print(streamlines[0])

    if one_node == two_node:
        print('paramater wrong ! one node or two node?')
    else:
        if one_node:
            return (ROI[top[0], top[1], top[2]] == 1) or ((ROI[bo[0], bo[1], bo[2]]) == 1)
        else:
            return (ROI[top[0], top[1], top[2]] == 1) and ((ROI[bo[0], bo[1], bo[2]])==1)

def GetThroughROI(streamlines, ROI_mask):
    for i in range(streamlines.shape[0]):
        dot1 = streamlines[i].astype('int')
        # print(dot1)
        # print(dot1.shape)
        # print(dot1[0])
        if ROI_mask[dot1[0], dot1[1], dot1[2]] == 1:
            #print('in!')
            return True
    return False

def reduct_seed_ROI(streamlines, ROI, one_node, two_node):

    new_streamlines = []


    for i in range(len(streamlines)):

        line = streamlines[i]
        if IsGrowFromROI(line, ROI, one_node, two_node):
            new_streamlines.append(line)

    return new_streamlines

def minus_ROI(streamlines, ROI):

    new_streamlines = []


    for i in range(len(streamlines)):

        line = streamlines[i]
        if not GetThroughROI(streamlines=line, ROI_mask=ROI):
            new_streamlines.append(line)

    return new_streamlines

def reg_streamline(streamlines, affine):

    new_streamlines = []


    for i in range(len(streamlines)):

        line = streamlines[i]
        #print( np.ones((line.shape[0], 1)).shape)
        new_line = np.dot(np.hstack((line, np.ones((line.shape[0], 1)))), affine[0:3, :].T)

        new_line = new_line.astype(np.int)
        new_streamlines.append(new_line)

    return new_streamlines

def reduct(streamlines, threshold=1):
    new_streamlines = []
    for i in range(len(streamlines)):
        line = streamlines[i]
        if line.shape[0] > threshold:
            new_streamlines.append(line)
    return new_streamlines

def select_by_ROI(ROI_mask, streamlines, GetThrough=True):
    new_streamlines = []
    for i in range(len(streamlines)):
        line = streamlines[i]
        if GetThroughROI(streamlines=line, ROI_mask=ROI_mask) == GetThrough:
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

def ROI_atlas_dipy(atlasobj, track_path):
    trk = load_trk(track_path, 'same')
    streamlines = trk.streamlines
    streamlines = reduct(streamlines)
    atlas = atlasobj.get_data(2)
    roi_feature = np.zeros(atlasobj.count)
    for i in range(1, atlasobj.count + 1):
        ROI_mask = atlas == i
        cc_streamlines = utils.target(streamlines, trk.affine, ROI_mask)
        cc_streamlines = Streamlines(cc_streamlines)
        roi_feature[i-1] = len(cc_streamlines)
        print('roi ', i, ' finished!', atlasobj.count, 'total')
    return roi_feature

def ROI_atlas(atlasobj, track_path=None, streamlines=None):
    atlas = atlasobj.get_data(2)
    streamlines = load_trk(track_path, 'same')
    streamlines.to_vox()
    streamlines = streamlines.streamlines
    streamlines = reduct(streamlines)

    roi_feature = np.zeros(atlasobj.count)

    for i in range(1, atlasobj.count + 1):
        ROI_mask = atlas == i
        cc_streamlines = select_by_ROI(ROI_mask=ROI_mask, streamlines=streamlines)
        roi_feature[i-1] = len(cc_streamlines)
        print('roi ', i, ' finished! ans = ', roi_feature[i-1])
    return roi_feature

def track_gen_net_work(atlas_path=None, atlas=None,
                       data_path=None, affine=None,
                       track_path=None, streamlines=None,
                       return_matrix=False, save_matrix=True, output_path=None):

    import scipy.io as scio

    if atlas_path != None:
        img_atlas = nib.load(atlas_path)
        labels = img_atlas.get_data()
        labels = labels.astype(int)
    else:
        labels = atlas

    if data_path != None:
        data, affine, hardi_img = load_nifti(data_path, return_img=True)

    if track_path == None:
        tracks = streamlines
    else:
        tracks = dwi.load_streamlines_from_trk(track_path)
        tracks = reduct(tracks)


    M, grouping = utils.connectivity_matrix(tracks, affine=affine, label_volume = labels,
                              return_mapping=True, mapping_as_streamlines=True)
    if save_matrix:
        scio.savemat(output_path, {'matrix': M})

    if return_matrix:
        return M

#assert len(other_streamlines) + len(cc_streamlines) == len(tracks)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='output: the streamline number of ROI')
    parser.add_argument('-ma', '--mask_path', default=None, help='mask file path')
    parser.add_argument('-t', '--track_path', default=None, help='track file path')
    parser.add_argument('-d', '--normdata_path', default=None)

    parser.add_argument('-n', '--name', default=None, help='the name of individual')
    parser.add_argument('-m', '--method', type=int, default='1', help='the tracking method')
    parser.add_argument('-a', '--atlas', default='aal', help='the atlas')
    parser.add_argument('-i', '--index', default=None, help='the index of ROI')

    parser.add_argument('-o', '--output', default='./Result/ROI2.json', help='output file path')

    args = parser.parse_args()
    print(args)
    method_index = args.method
    mask_path = args.mask_path
    track_path = args.track_path
    normdata_path = args.normdata_path
    name = args.name
    atlas = args.atlas
    output = args.output
    index = args.index

    cal_ROI_num(mask_path, track_path, normdata_path, name, method_index, atlas, index, output)
