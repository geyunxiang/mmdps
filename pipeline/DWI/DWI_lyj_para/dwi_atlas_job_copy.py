
import json
from sys import exec_prefix
from dipy.io.streamline import load_trk
from dipy.io.image import load_nifti_data
from mmdps.sigProcess.DWI.tracking_plus.utils import ROI_atlas
import scipy.io as sio
import numpy as np
from dwi_calc_base import dwi_calc_base
from mmdps.proc.atlas import get
import os


class dwi_atlas_calc(dwi_calc_base):
    def __init__(self) -> None:
        super().__init__()
        self._atlasConfigName = 'atlas_config.json'
        self._atlasConfigKey = ['atlas_path', 'track_root', 'output_root',
                                'feature_list_output_filename', 'matrix_output_filename', 'tracking_method']
        self.fromjson(self.name2path(self._atlasConfigName),
                      self._atlasConfigKey)

    def calc(self):
        atlas_path = self.argsDict['atlas_path']
        track_root = self.argsDict['track_root']
        output_root = self.argsDict['output_root']
        output_file = self.argsDict['feature_list_output_filename']
        tracking_method = self.argsDict['tracking_method']

        _atlasobj = None
        if not os.path.isfile(atlas_path):
            _tmp = atlas_path.split()
            _atlasobj = get(_tmp[0])
            if _tmp[1]+'mm' in _atlasobj.volumes.keys():
                atlas_path = _atlasobj.volumes[_tmp[1]+'mm']['niifile']
            else:
                raise Exception('please assign the atlas\'s resolution' )
        else:
            _tmp = atlas_path.split('/')[-1].split('.')
            _atlasobj = get(_tmp[0])

        atlas = load_nifti_data(atlas_path).astype('int')

        # feature_list = {}
        name = ''
        track_path = track_root+'/tractogram_'+tracking_method+'_'+name+'.trk'
        if not os.path.isfile(track_path):
            raise Exception('Such file not exist: '+os.path.join(os.getcwd(),track_path))

        track = load_trk(track_path, 'same')
        track.to_vox()
        streamlines = track.streamlines
        
        output_path = os.path.join(output_root,_atlasobj.name)
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        
        roi_feature = ROI_atlas(
            streamlines=streamlines, atlas=atlas, affine=np.eye(4))
        # feature_list[name] = roi_feature

        sio.savemat(output_path+'/'+output_file, roi_feature)


if __name__ == '__main__':

    dwi_a = dwi_atlas_calc()
    dwi_a.calc()
