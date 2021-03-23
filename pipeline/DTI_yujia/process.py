import os
import argparse
import json
from pipeline.DTI_yujia.tracking_plus import tracking_method
from pipeline.DTI_yujia.tracking_plus.ROI import ROI_atlas, track_gen_net_work

from dipy.core.gradients import gradient_table
from dipy.data import get_fnames
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti, load_nifti_data, save_nifti
import scipy.io as sio

from pipeline.DTI_yujia.tracking_plus.tracking_method import get_data

import dipy.reconst.dti as dti
import time
import numpy as np

def get_FA_MD():
    time0 = time.time()

    data, affine = load_nifti('normalized_pDWI.nii.gz')
    bvals, bvecs = read_bvals_bvecs('DWI.bval', 'DWI.bvec')
    gtab = gradient_table(bvals, bvecs)
    #head_mask = load_nifti_data(data_path + '/' + brain_mask)

    print(data.shape)
    print('begin modeling!, time:', time.time() - time0)

    tenmodel = dti.TensorModel(gtab)
    tenfit = tenmodel.fit(data)

    from dipy.reconst.dti import fractional_anisotropy
    print('begin calculating FA!, time:', time.time() - time0)

    FA = fractional_anisotropy(tenfit.evals)

    FA[np.isnan(FA)] = 0
    #FA = FA * head_mask
    save_nifti('FA.nii.gz', FA.astype(np.float32), affine)

    # print('begin calculating MD!, time:', time.time() - time0)
    MD1 = dti.mean_diffusivity(tenfit.evals)
    #MD1 = MD1*head_mask
    save_nifti('MD.nii.gz', MD1.astype(np.float32), affine)

    print('Over!, time:', time.time() - time0)

    return FA, MD1

def process():
    parser = argparse.ArgumentParser(description="tracking, analys, in batches")
    parser.add_argument('-f', '--config_file', default='./config.json', help='config file')
    parser.add_argument('-t', '--HasTrack', default=False, type=int, help='did track exist?')
    parser.add_argument('-a', '--NeedAtlas', default=True, type=int, help='need extract feature?')
    parser.add_argument('-m', '--need_matrix', default=False, type=int)
    parser.add_argument('-fa', '--FA_MD', default=True, type=int)

    args = parser.parse_args()
    print(args)
    config_file =args.config_file
    HasTrack = args.HasTrack
    NeedAtlas = args.NeedAtlas
    NeedMatrix = args.need_matrix
    FA_MD = args.FA_MD

    with open(config_file , 'r') as fileR:  # open config file
        strF = fileR.read()
        if len(strF) == 0:
            print('wrong! no content in config file!')
        else:
            R = json.loads(strF)
            data_root = R['data_root']
            name_list_path = R['name_list']
            result_folder = R['result_folder']
            norm = R['norm_DWI_name']
            brain_mask = R['brain_mask_name']
            FA = R['FA_name']
            bval = R['bval_name']
            bvec = R['bvec_name']
            atlas_path = R['atlas_file']
            output = R['mat_output_path']
            output_matrix = R['output_matrix']
    print(name_list_path)
    with open(name_list_path, 'r') as fileR:  # open name list file
        #strF = fileR.read()
        if len(strF) == 0:
            print('wrong! no content in name list!')
    name_list = []
    with open(name_list_path, 'r') as fileR:
        for line in fileR.readlines():
            name_list.append(line.strip())

    feature_list = {}
    Matrix_list = {}
    index = 0
    print(name_list)

    for name in name_list:
        index = index + 1
        data_path = data_root+'/'+name
        print(data_path)
        print('No.', index, name, 'begin!')
        
        if not os.path.exists(result_folder+'/'+name):
            os.makedirs(result_folder+'/'+name)
        print('loading data!')
        data, affine, img = load_nifti(data_path+'/'+norm, return_img=True)
        
        if FA_MD == 0:
            get_FA_MD(name=name, data_path=data_path)
        
        if not HasTrack:
            bvals, bvecs = read_bvals_bvecs(data_path + '/' + bval, data_path + '/' + bvec)
            gtab = gradient_table(bvals, bvecs)
            head_mask = load_nifti_data(data_path + '/' + brain_mask)
            FA_data = load_nifti_data(data_path + '/' + FA)
            labels = (FA_data > 0.15) * 2
            data_list = {'DWI': data, 'affine': affine, 'img': img, 'labels': labels,
                         'gtab': gtab, 'head_mask': head_mask}
            #eed = load_nifti_data('../data/atlas/bnatlas/ROI_167.nii.gz')
            #seed = load_nifti_data('D:\ZhangGuangzhu_DTI\LYBb0space/231LYB_pre_B=1000/noinjured2.nii.gz')
            #plant73 = load_nifti_data('./exp4\seed/b0_normalized_aal_1_73.nii.gz')
            #plant75 = load_nifti_data('./exp4\seed/b0_normalized_aal_1_75.nii.gz')
            tracking_method.probal(name=name, data_list=data_list,
                                     output_path=result_folder,  Threshold=0.15)#, seed=seed)#, one_node=True)
        track_path = result_folder+'/tractogram_probabilistic_'+name+'.trk'
        #print(streamlines)

        if NeedAtlas:
            print('begin extracting feature!')
            roi_feature = ROI_atlas(affine=affine, DWI=data, atlas_path=atlas_path,
                                track_path=track_path)
            feature_list[name] = roi_feature
        print(name, 'done!', index, '/', len(name_list), 'finished')

        if NeedMatrix:
            print('making matrix!')
            Matrix_list[name] = track_gen_net_work(affine=affine, atlas_path=atlas_path,
                                                   track_path=track_path, return_matrix=True,
                                                   save_matrix=False)

    if NeedAtlas:
        sio.savemat(output, feature_list)
    if NeedMatrix:
        sio.savemat(output_matrix, Matrix_list)

if __name__ == '__main__':
    data, affine, img = load_nifti('normalized_pDWI.nii.gz', return_img = True)

    get_FA_MD()

    bvals, bvecs = read_bvals_bvecs('DWI.bval', 'DWI.bvec')
    gtab = gradient_table(bvals, bvecs)
    head_mask = load_nifti_data('normalized_mask.nii.gz')
    FA_data = load_nifti_data('FA.nii.gz')

    labels = (FA_data > 0.15) * 2

    data_list = {'DWI': data, 'affine': affine, 'img': img, 'labels': labels, 'gtab': gtab, 'head_mask': head_mask}
    # eed = load_nifti_data('../data/atlas/bnatlas/ROI_167.nii.gz')
    # seed = load_nifti_data('D:\ZhangGuangzhu_DTI\LYBb0space/231LYB_pre_B=1000/noinjured2.nii.gz')
    # plant73 = load_nifti_data('./exp4\seed/b0_normalized_aal_1_73.nii.gz')
    # plant75 = load_nifti_data('./exp4\seed/b0_normalized_aal_1_75.nii.gz')
    tracking_method.probal(data_list = data_list, Threshold = 0.15)

    track_path = 'tractogram_probabilistic.trk'
    atlas_path = 'E:/pythonmodules/mmdps/atlas/aal/aal_2.nii'
    print('begin extracting feature!')
    roi_feature = ROI_atlas(atlas_path = atlas_path, track_path = track_path)
    feature_list[name] = roi_feature
    print(name, 'done!', index, '/', len(name_list), 'finished')

    print('making matrix!')
    Matrix_list[name] = track_gen_net_work(affine = affine, atlas_path = atlas_path, track_path = track_path, return_matrix = True, save_matrix = False)
