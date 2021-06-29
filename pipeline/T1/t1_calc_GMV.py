import os
import t1_niicalc as niicalc
from mmdps.proc import atlas
from mmdps.util.loadsave import load_nii, save_csvmat

if __name__ == '__main__':
	img = load_nii('../grey.hdr')
	curatlas = atlas.getbywd()
	atlasimg = load_nii(curatlas.get_volume('1mm')['niifile'])
	res = niicalc.calc_region_mean(img, curatlas, atlasimg)
	save_csvmat(os.path.join('t1mean', 'greyvolume.csv'), res)
