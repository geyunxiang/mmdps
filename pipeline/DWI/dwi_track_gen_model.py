"""
Generate tracking model

Input: brain mask, DWI data bval bvec
Output: pickles, affine sphere ten ind
"""

import nibabel as nib
from mmdps.util import dwi

from dipy.reconst.dti import TensorModel, quantize_evecs
from dipy.data import get_sphere
from dipy.io import pickles

class Struct:
    pass

def track_gen_model(brain_mask_file, dwi_data_file, dwi_bval_file, dwi_bvec_file):
    img_mask = nib.load(brain_mask_file)
    img, gtab = dwi.get_dwi_img_gtab(dwi_data_file, dwi_bval_file, dwi_bvec_file)
    data_mask = img_mask.get_data()
    affine = img.get_affine()
    data = img.get_data()

    model = TensorModel(gtab)
    ten = model.fit(data, mask=data_mask)
    sphere = get_sphere('symmetric724')
    ind = quantize_evecs(ten.evecs, sphere.vertices)

    p = Struct()
    p.affine = affine
    p.sphere = sphere
    p.ten = ten
    p.ind = ind
    return p

if __name__ == '__main__':
    import sys
    print('dwi_track_gen_model, sys.argv: ', sys.argv)
    if len(sys.argv) == 5:
        brain_mask = sys.argv[1]
        dwi_data = sys.argv[2]
        dwi_bval = sys.argv[3]
        dwi_bvec = sys.argv[4]
        outp = track_gen_model(brain_mask, dwi_data, dwi_bval, dwi_bvec)
        pickles.save_pickle('track_gen_model.pickle', outp)
