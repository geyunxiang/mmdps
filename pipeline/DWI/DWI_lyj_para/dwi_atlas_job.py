from mmdps.util import path
from dipy.io.streamline import load_trk
from dipy.io.image import load_nifti_data
from mmdps.sigProcess.DWI.tracking_plus.utils import ROI_atlas
import scipy.io as sio
import numpy as np
from dwi_calc_base import dwi_calc_base
import os


class dwi_atlas_calc(dwi_calc_base):
    def __init__(self) -> None:
        super().__init__()
        self._atlasConfigName = 'atlas_config.json'
        self._atlasConfigKey = ['atlas_volume','track_root', 
                                'feature_ROI_filename', 'tracking_method']
        self.fromjson(self.name2path(self._atlasConfigName),
                      self._atlasConfigKey)

    def calc(self):
        atlas_volume = self.argsDict['atlas_volume']
        track_root = self.argsDict['track_root']
        output_root = self.argsDict['output_root']
        output_file = self.argsDict['feature_ROI_filename']
        tracking_method = self.argsDict['tracking_method']

        _atlasobj = path.curatlas()
        atlas_path = _atlasobj.get_volume(atlas_volume)['niifile']
        output_file = _atlasobj.name+'_'+output_file
        atlas = load_nifti_data(atlas_path).astype('int')

        feature_list = {}
        name = ''
        track_path = track_root+'/tractogram_'+tracking_method+'_'+name+'.trk'
        if not os.path.isfile(track_path):
            raise Exception('Such file not exist: '+os.path.join(os.getcwd(),track_path))

        track = load_trk(track_path, 'same')
        track.to_vox()
        streamlines = track.streamlines
        
        output_path = output_root
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        
        roi_feature = ROI_atlas(
            streamlines=streamlines, atlas=atlas, affine=np.eye(4))
        feature_list['roi_feature'] = roi_feature

        sio.savemat(output_path+'/'+output_file, feature_list)


if __name__ == '__main__':
    dwi_a = dwi_atlas_calc()
    dwi_a.calc()
