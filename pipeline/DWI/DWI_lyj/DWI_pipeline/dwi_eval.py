

import argparse
import json
from dipy.io.streamline import load_trk
from dipy.io.image import load_nifti_data, save_nifti
from tracking_plus.eval_ import LiFE_new, get_evals_map, LiFE
from tracking_plus.utils import get_data
import os



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="eval tracking")
    parser.add_argument('-f1', '--basic_config_file', default='./basic_config.json', help='basic config file')
    parser.add_argument('-f2', '--eval_config_file', default='./eval_config.json', help='eval config file')

    args = parser.parse_args()
    print(args)
    eval_config_file = args.eval_config_file
    basic_config_file = args.basic_config_file

    with open(basic_config_file, 'r') as fileR:  # open config file

        strF = fileR.read()
        if len(strF) == 0:
            print('wrong! no content in config file!')
        else:
            R = json.loads(strF)
            data_root = R['data_root']
            name_list_path = R['name_list']
            norm = R['norm_DWI_name']
            brain_mask = R['brain_mask_name']
            bval = R['bval_name']
            bvec = R['bvec_name']


    with open(eval_config_file, 'r') as fileR:  # open config file

        strF = fileR.read()
        if len(strF) == 0:
            print('wrong! no content in eval config file!')
        else:
            R = json.loads(strF)
            track_root = R['track_root']
            tracking_method = R['tracking_method']
            name_list_path = R['name_list']
            eval_method = int(R['eval_method'])
            evals_map_name = R['evals_map_name']
            output_file = R['output_file']

    name_list = []
    with open(name_list_path, 'r') as fileR:
        for line in fileR.readlines():
            name_list.append(line.strip())

    index = 0
    print('eval begin')

    for name in name_list:
        index = index + 1
        track_path = track_root + '/' + name + '/tractogram_' + tracking_method + '_' + name + '.trk'
        track = load_trk(track_path, 'same')
        track.to_vox()
        streamlines = track.streamlines

        data_path = data_root + '/' + name
        data, affine, img, gtab, head_mask, FA = get_data(data_path=data_path,
                                                              norm=norm, bval=bval, bvec=bvec,
                                                              mask=brain_mask, FA='FA.nii.gz')

        if eval_method==0:
            evaluation = LiFE(streamlines=streamlines, gtab=gtab, data=data)
        else:

            if evals_map_name == 'None':
                evals_map, index_map = get_evals_map(gtab, data, head_mask, FA)
                save_nifti(data_path+'/'+'evals_map.nii.gz', evals_map, affine)
                save_nifti(data_path + '/' + 'index_map.nii.gz', index_map, affine)
            else:
                evals_map = load_nifti_data(data_path+'/'+evals_map_name)
            evaluation = LiFE_new(streamlines=streamlines, gtab=gtab, data=data,
                  eval_map=evals_map)



        output_name = name+'_'+tracking_method+'_eval'+str(eval_method)+'.nii.gz'

        if not os.path.exists(output_file+'/'+name):
            os.makedirs(output_file+'/'+name)
        save_nifti(output_file+'/'+name+'/'+output_name,data=evaluation, affine=affine)





        print('No.', index, name, 'finished!')

