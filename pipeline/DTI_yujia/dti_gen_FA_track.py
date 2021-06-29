from tracking_plus import tracking_method

from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti, load_nifti_data, save_nifti

import dipy.reconst.dti as dti
import time
import numpy as np

def get_FA_MD():
    time0 = time.time()

    data, affine = load_nifti('normalized_pDWI.nii.gz')
    bvals, bvecs = read_bvals_bvecs('DWI.bval', 'DWI.bvec')
    gtab = gradient_table(bvals, bvecs)
    #head_mask = load_nifti_data(data_path + '/' + brain_mask)

    print(data.shape)
    print('begin modeling!, time:', time.time() - time0)

    tenmodel = dti.TensorModel(gtab)
    tenfit = tenmodel.fit(data)

    from dipy.reconst.dti import fractional_anisotropy
    print('begin calculating FA!, time:', time.time() - time0)

    FA = fractional_anisotropy(tenfit.evals)

    FA[np.isnan(FA)] = 0
    #FA = FA * head_mask
    save_nifti('FA.nii.gz', FA.astype(np.float32), affine)

    # print('begin calculating MD!, time:', time.time() - time0)
    MD1 = dti.mean_diffusivity(tenfit.evals)
    #MD1 = MD1*head_mask
    save_nifti('MD.nii.gz', MD1.astype(np.float32), affine)

    print('Over!, time:', time.time() - time0)

    return FA, MD1

if __name__ == '__main__':
    data, affine, img = load_nifti('normalized_pDWI.nii.gz', return_img = True)

    get_FA_MD()

    bvals, bvecs = read_bvals_bvecs('DWI.bval', 'DWI.bvec')
    gtab = gradient_table(bvals, bvecs)
    head_mask = load_nifti_data('normalized_mask.nii.gz')
    FA_data = load_nifti_data('FA.nii.gz')

    labels = (FA_data > 0.15) * 2

    data_list = {'DWI': data, 'affine': affine, 'img': img, 'labels': labels, 'gtab': gtab, 'head_mask': head_mask}
    # eed = load_nifti_data('../data/atlas/bnatlas/ROI_167.nii.gz')
    # seed = load_nifti_data('D:\ZhangGuangzhu_DTI\LYBb0space/231LYB_pre_B=1000/noinjured2.nii.gz')
    # plant73 = load_nifti_data('./exp4\seed/b0_normalized_aal_1_73.nii.gz')
    # plant75 = load_nifti_data('./exp4\seed/b0_normalized_aal_1_75.nii.gz')
    tracking_method.probal(data_list = data_list, Threshold = 0.15)
