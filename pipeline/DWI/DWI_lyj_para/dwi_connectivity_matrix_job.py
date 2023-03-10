from mmdps.util import path
import json
from dipy.io.streamline import load_trk
from dipy.io.image import load_nifti_data
from mmdps.sigProcess.DWI.tracking_plus.utils import track_gen_net_work
import scipy.io as sio
import numpy as np
from dwi_calc_base import dwi_calc_base
import os


class dwi_connectivity_matrix_calc(dwi_calc_base):
    def __init__(self):
        super().__init__()
        self._atlasConfigName = 'atlas_config.json'
        self._atlasConfigKey = ['atlas_volume','track_root', 
                                'feature_connectivity_filename', 'tracking_method']
        self.fromjson(self.name2path(self._atlasConfigName),
                      self._atlasConfigKey)

    def calc(self):
     
        atlas_volume = self.argsDict['atlas_volume']
        track_root = self.argsDict['track_root']
        output_root = self.argsDict['output_root']
        output_file = self.argsDict['feature_connectivity_filename']
        tracking_method = self.argsDict['tracking_method']

        _atlasobj = path.curatlas()
        atlas_path = _atlasobj.get_volume(atlas_volume)['niifile']
        output_file = _atlasobj.name+'_'+output_file
        print(atlas_path)
        atlas = load_nifti_data(atlas_path).astype('int')

        Matrix_list={}
        name = ''
        track_path = track_root+'/tractogram_'+tracking_method+'_'+name+'.trk'
        if not os.path.isfile(track_path):
            raise Exception('Such file not exist: '+os.path.join(os.getcwd(),track_path))

        track = load_trk(track_path, 'same')
        track.to_vox()
        streamlines = track.streamlines

        matrix = track_gen_net_work(streamlines=streamlines, atlas=atlas, affine=np.eye(4))
        Matrix_list['dwi_connectivity'] = matrix

        sio.savemat(output_root+'/'+output_file, Matrix_list)







if __name__ == '__main__':

    dwi_cm = dwi_connectivity_matrix_calc()
    dwi_cm.calc()


    