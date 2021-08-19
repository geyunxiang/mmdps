from dipy.io.streamline import load_trk
from dipy.io.image import load_nifti_data, save_nifti
from mmdps.sigProcess.DWI.tracking_plus.eval_ import LiFE_new, get_evals_map, LiFE
from mmdps.sigProcess.DWI.tracking_plus.utils import get_data
import os
from dwi_calc_base import dwi_calc_base

class dwi_eval_calc(dwi_calc_base):
    def __init__(self):
        super().__init__()
        self._evalConfigName = 'eval_config.json'
        self._evalConfigKey = ['track_root','tracking_method','eval_method','evals_map_name','output_file',]
        self.fromjson(self.name2path(self._evalConfigName),self._evalConfigKey)

    def calc(self):


        norm = self.argsDict['norm_DWI_name']
        brain_mask = self.argsDict['brain_mask_name']
        bval = self.argsDict['bval_name']
        bvec = self.argsDict['bvec_name']

        track_root = self.argsDict['track_root']
        tracking_method = self.argsDict['tracking_method']
        eval_method = int(self.argsDict['eval_method'])
        evals_map_name = self.argsDict['evals_map_name']
        output_file = self.argsDict['output_file']

        name = ''
        track_path = track_root+'/tractogram_'+tracking_method+'_'+name+'.trk'
        if not os.path.isfile(track_path):
            raise Exception('Such file not exist: '+os.path.join(os.getcwd(),track_path))
        track = load_trk(track_path, 'same')
        track.to_vox()
        streamlines = track.streamlines

        data_path = './'
        data, affine, _, gtab, head_mask, FA = get_data(data_path=data_path,
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
        
        
        if not os.path.exists(output_file):
            os.makedirs(output_file)
        output_name = tracking_method+'_eval'+str(eval_method)+'.nii.gz'

        print(os.getcwd(),output_file+'/'+output_name)
        save_nifti(output_file+'/'+output_name,data=evaluation, affine=affine)





if __name__ == '__main__':
    # track_path = '/home/mmdp/Zhangziliang/GitWorkspace/DWI_DATA/baihanxiang_20190211/tracking_result/tractogram_EuDX_.trk'
    # track = load_trk(track_path, 'same')
    # track.to_vox()
    # streamlines = track.streamlines
    
    # data_path = '/home/mmdp/Zhangziliang/GitWorkspace/DWI_DATA/baihanxiang_20190211'
    # data, affine, _, gtab, head_mask, FA = get_data(data_path=data_path,
    #                                                           norm="normalized_pDWI.nii.gz", bval="DWI.bval", bvec="DWI.bvec",
    #                                                           mask="normalized_mask.nii.gz", FA='FA.nii.gz')

    # evaluation = LiFE(streamlines=streamlines, gtab=gtab, data=data)


    

    dwi_e = dwi_eval_calc()
    dwi_e.calc()