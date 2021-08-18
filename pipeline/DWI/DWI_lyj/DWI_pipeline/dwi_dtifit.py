import json
import argparse
from tracking_plus.utils import dwi_dtifit



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="tracking, analys, in batches")
    parser.add_argument('-f', '--config_file', default='./basic_config.json', help='basic config file')

    args = parser.parse_args()
    print(args)
    config_file = args.config_file

    with open(config_file, 'r') as fileR:  # open config file

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

    index=0

    for name in name_list:
        data_path = data_root + '/' + name
        print('No.', index, name, 'begin!')

        dwi_dtifit(data_path=data_path, norm=norm, bval=bval, bvec=bvec,
                   mask=brain_mask)