import argparse
import json
from dipy.io.streamline import load_trk
from dipy.io.image import load_nifti_data
from tracking_plus.utils import track_gen_net_work
import scipy.io as sio
import numpy as np

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="tracking")
    parser.add_argument('-f2', '--atlas_config_file', default='./atlas_config.json', help='atlas config file')
    parser.add_argument('-f1', '--basic_config_file', default='./basic_config.json', help='basic config file')

    args = parser.parse_args()
    print(args)
    basic_config_file = args.basic_config_file
    atlas_config_file = args.atlas_config_file

    with open(basic_config_file, 'r') as fileR:  # open config file

        strF = fileR.read()
        if len(strF) == 0:
            print('wrong! no content in config file!')
        else:
            R = json.loads(strF)
            name_list_path = R['name_list']

    with open(atlas_config_file, 'r') as fileR:  # open config file

        strF = fileR.read()
        if len(strF) == 0:
            print('wrong! no content in atlas config file!')
        else:
            R = json.loads(strF)
            atlas_path = R['atlas_path']
            track_root = R['track_root']
            output_root = R['output_root']
            output_file = R['matrix_output_filename']
            tracking_method = R['tracking_method']

    atlas = load_nifti_data(atlas_path).astype('int')
    name_list = []
    with open(name_list_path, 'r') as fileR:
        for line in fileR.readlines():
            name_list.append(line.strip())

    index = 0
    Matrix_list={}
    print('connectivity matrix begin')

    for name in name_list:
        index = index + 1
        track_path = track_root + '/' + name + '/tractogram_' + tracking_method + '_' + name + '.trk'
        track = load_trk(track_path, 'same')
        track.to_vox()
        streamlines = track.streamlines

        matrix = track_gen_net_work(streamlines=streamlines, atlas=atlas, affine=np.eye(4))
        Matrix_list[name] = matrix

        print('No.', index, name, 'finished!')

        sio.savemat(output_root+'/'+name+'/'+output_file, Matrix_list)