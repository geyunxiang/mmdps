import os
import dwi_niicalc as niicalc
from mmdps.proc import atlas
from mmdps.util.loadsave import load_nii, save_csvmat

def calc_attr(attr_name):
    img = load_nii('../iso2.0_dtifitresult_{}.nii.gz'.format(attr_name))
    atlasobj = atlas.getbywd()
    atlasimg = load_nii(os.path.join('nativespace', 'wtemplate_2.nii.gz'))
    res = niicalc.calc_region_mean(img, atlasobj, atlasimg)
    save_csvmat(os.path.join('nativespace', 'mean{}.csv'.format(attr_name)), res)

if __name__ == '__main__':
    calc_attr('FA')
    calc_attr('MD')
    calc_attr('AD')
    calc_attr('RD')
