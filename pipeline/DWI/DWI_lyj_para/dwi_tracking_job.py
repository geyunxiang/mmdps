
from mmdps.sigProcess.DWI.tracking_plus import tracking_
import json
import os
from dwi_calc_base import dwi_calc_base
from dipy.io.image import load_nifti_data

# current working directory

class dwi_tracking_calc(dwi_calc_base):
    def __init__(self) -> None:
        super().__init__()
        self._trackingConfigName = 'tracking_config.json'
        self._trackingConfigKey = ['tracking_method','result_folder','seed_mask_file','FA_name','StoppingThreshold','evals_map_name','index_map_name']
        self.fromjson(self.name2path(self._trackingConfigName),self._trackingConfigKey)

    def calc(self):
        norm = self.argsDict['norm_DWI_name']
        brain_mask = self.argsDict['brain_mask_name']
        bval = self.argsDict['bval_name']
        bvec = self.argsDict['bvec_name']
        tracking_method = int(self.argsDict['tracking_method'])
        result_folder = self.argsDict['result_folder']
        seed_mask = self.argsDict['seed_mask_file']
        FA = self.argsDict['FA_name']
        StoppingTh=float(self.argsDict['StoppingThreshold'])
        evals_map_name = self.argsDict['evals_map_name']
        index_map_name = self.argsDict['index_map_name']

        data_path = './'
        output_folder = './'+result_folder 
        name = ''

        if seed_mask=='None':
            seed_mask='.'
        else:
            seed_mask=load_nifti_data(seed_mask).astype('int')

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



if __name__ == '__main__':
    d_track = dwi_tracking_calc()
    d_track.calc()


