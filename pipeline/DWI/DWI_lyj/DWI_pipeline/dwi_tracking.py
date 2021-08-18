
from tracking_plus.utils import dwi_dtifit, ROI_atlas, track_gen_net_work
from tracking_plus import tracking_
from tracking_plus.eval_ import get_evals_map
import argparse
import json
import scipy.io as sio
import os

from dipy.io.image import load_nifti_data

# current working directory


if __name__ == '__main__':
 
    parser = argparse.ArgumentParser(description="tracking")
    parser.add_argument('-f2', '--tracking_config_file', default='./tracking_config.json', help='tracking config file')
    parser.add_argument('-f1', '--basic_config_file', default='./basic_config.json', help='basic config file')

    args = parser.parse_args()
    print(args)
    basic_config_file = args.basic_config_file
    tracking_config_file = args.tracking_config_file

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

    name_list = []
    with open(name_list_path, 'r') as fileR:
        for line in fileR.readlines():
            name_list.append(line.strip())


    with open(tracking_config_file, 'r') as fileR:  # open config file

        strF = fileR.read()
        if len(strF) == 0:
            print('wrong! no content in tracking config file!')
        else:
            R = json.loads(strF)
            tracking_method = int(R['tracking_method'])
            result_folder = R['result_folder']
            seed_mask = R['seed_mask_file']
            FA = R['FA_name']
            StoppingTh=float(R['StoppingThreshold'])
            evals_map_name = R['evals_map_name']
            index_map_name = R['index_map_name']

    if seed_mask=='None':
        seed_mask='.'
    else:
        seed_mask=load_nifti_data(seed_mask).astype('int')


    index=0

    for name in name_list:

        index = index + 1

        data_path = data_root + '/' + name

        print('No.', index, name, 'begin!')

        output_folder = result_folder + '/' + name
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if tracking_method==1:
            tracking_.basic_tracking(name=name, data_path=data_path,
                         norm=norm, bval=bval, bvec=bvec, FA=FA, mask=brain_mask,
                         output_path=output_folder, Threshold=StoppingTh, data_list=None, seed=seed_mask)
        if tracking_method==2:
            tracking_.probal(name=name, data_path=data_path,
                         norm=norm, bval=bval, bvec=bvec, FA=FA, mask=brain_mask,
                         output_path=output_folder, Threshold=StoppingTh, data_list=None, seed=seed_mask)
        if tracking_method==3:
            tracking_.determine(name=name, data_path=data_path,
                         norm=norm, bval=bval, bvec=bvec, FA=FA, mask=brain_mask,
                         output_path=output_folder, Threshold=StoppingTh, data_list=None, seed=seed_mask)
        if tracking_method==4:
            tracking_.sfm_tracking(name=name, data_path=data_path,
                         norm=norm, bval=bval, bvec=bvec, FA=FA, mask=brain_mask,
                         output_path=output_folder, Threshold=StoppingTh, data_list=None, seed=seed_mask)
        if tracking_method==5:

            if evals_map_name=='None':
                evals_map=None
            else:
                evals_map = load_nifti_data(data_path+'/'+evals_map_name)

            if index_map_name=='None':
                index_map=None
            else:
                index_map = load_nifti_data(data_path + '/' + evals_map_name)


            tracking_.sfm_new(name=name, data_path=data_path,
                         norm=norm, bval=bval, bvec=bvec, FA=FA, mask=brain_mask,
                         output_path=output_folder, Threshold=StoppingTh, data_list=None, seed=seed_mask,
                         evals_map=evals_map, index_map=index_map)




