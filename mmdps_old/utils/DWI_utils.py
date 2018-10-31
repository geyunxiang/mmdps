import os.path
import nibabel as nib
from dipy.align.reslice import reslice
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from dipy.viz import fvtk

def get_dwi_file_path(folder, niiname, gz=False):
	fdwi = os.path.join(folder, niiname+'.nii')
	if gz:
		fdwi = fdwi + '.gz'
	fbval = os.path.join(folder, niiname+'.bval')
	fbvec = os.path.join(folder, niiname+'.bvec')
	return fdwi, fbval, fbvec

def get_dwi_img_gtab(fdwi, fbval, fbvec):
	img = nib.load(fdwi)
	bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
	gtab = gradient_table(bvals, bvecs)
	return img, gtab

def get_fvtk_streamlines_actor(streamlines):
	streamlines_actor = fvtk.line(streamlines)
	return streamlines_actor

def save_streamlines_to_trk(streamlines, affine, fileobj):
	tracto = nib.streamlines.Tractogram(streamlines, affine_to_rasmm=affine)
	trkfile = nib.streamlines.TrkFile(tracto)
	trkfile.save(fileobj)

def load_TrkFile(fileobj):
	trkfile = nib.streamlines.TrkFile.load(fileobj)
	return trkfile

def load_streamlines_from_trk(fileobj):
	trkfile = load_TrkFile(fileobj)
	return trkfile.streamlines

def reslice_img(img, new_zooms):
	data = img.get_data()
	affine = img.get_affine()
	zooms = img.get_header().get_zooms()[:3]
	data2, affine2 = reslice(data, affine, zooms, new_zooms)
	new_img = nib.Nifti1Image(data2.astype('int16'), affine2)
	print('reslice_img;', 'old_zooms:', zooms, 'new_zooms:', new_zooms)
	return new_img
	
