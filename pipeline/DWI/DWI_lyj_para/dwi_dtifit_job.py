import json
from mmdps.sigProcess.DWI.tracking_plus.utils import dwi_dtifit
from dwi_calc_base import dwi_calc_base



class dwi_dtifit_Calc(dwi_calc_base):
    def __init__(self):
        super().__init__()


    def calc(self):
        norm = self.argsDict['norm_DWI_name']
        brain_mask = self.argsDict['brain_mask_name']
        bval = self.argsDict['bval_name']
        bvec = self.argsDict['bvec_name']
        dwi_dtifit(data_path='./', norm=norm, bval=bval, bvec=bvec,mask=brain_mask)

    

        

if __name__ == '__main__':
    dwi_d = dwi_dtifit_Calc()
    dwi_d.calc()