from mmdps.util import dwi
import nibabel as nib

from dipy.reconst.dti import TensorModel
# from dipy.reconst.shm import CsaOdfModel
from dipy.direction import peaks_from_model
from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion
from dipy.tracking.local_tracking import LocalTracking
from dipy.tracking.streamline import Streamlines
from dipy.tracking.utils import random_seeds_from_mask
from dipy.data import get_sphere

import numpy as np

from dipy.direction import peaks
from dipy.reconst import shm
from dipy.tracking import utils
from dipy.tracking.stopping_criterion import BinaryStoppingCriterion


def track_gen_model(brain_mask_file, dwi_data_file, dwi_bval_file, dwi_bvec_file):
	img_mask = nib.load(brain_mask_file)
	img, gtab = dwi.get_dwi_img_gtab(dwi_data_file, dwi_bval_file, dwi_bvec_file)
	data_mask = img_mask.get_fdata()
	affine = img.affine
	data = img.get_fdata()

	sphere = get_sphere('symmetric724')
	model = TensorModel(gtab)
	tensor_model = model.fit(data, mask=data_mask)
	peaks = peaks_from_model(model, data, sphere, relative_peak_threshold=.8, min_separation_angle=45, mask=data_mask)
	stopping_criterion = ThresholdStoppingCriterion(tensor_model.fa, 0.2)

	streamlines_generator = LocalTracking(peaks, stopping_criterion, seeds = random_seeds_from_mask(data_mask, img_mask.affine, 10**5*5, seed_count_per_voxel = False), affine=affine, step_size=.5)
	# Generate streamlines object
	streamlines = Streamlines(streamlines_generator)
	with open('raw_track.trk', 'wb') as ftrkout:
		dwi.save_streamlines_to_trk(streamlines, affine, ftrkout)

def track_gen_model_tutorial(brain_mask_file, dwi_data_file, dwi_bval_file, dwi_bvec_file, label_file):
	img_mask = nib.load(brain_mask_file)
	img, gtab = dwi.get_dwi_img_gtab(dwi_data_file, dwi_bval_file, dwi_bvec_file)
	data_mask = img_mask.get_fdata()
	affine = img.affine
	data = img.get_fdata()

	sphere = get_sphere('symmetric724')
	csamodel = shm.CsaOdfModel(gtab, 6)
	csapeaks = peaks.peaks_from_model(model=csamodel, data=data, sphere=sphere, relative_peak_threshold=.8, min_separation_angle=45, mask=data_mask)
	seeds_affine = np.eye(4)
	seeds = utils.seeds_from_mask(data_mask, seeds_affine, density=1)
	stopping_criterion = BinaryStoppingCriterion(data_mask)

	streamline_generator = LocalTracking(csapeaks, stopping_criterion, seeds, affine=seeds_affine, step_size=0.5)
	streamlines = Streamlines(streamline_generator)

	img_label = nib.load(label_file)
	labels = img_label.get_fdata()
	M, grouping = utils.connectivity_matrix(streamlines, affine, labels.astype(np.uint8), return_mapping=True, mapping_as_streamlines=True)
	M[:3, :] = 0
	M[:, :3] = 0
	import matplotlib.pyplot as plt

	plt.imshow(np.log1p(M), interpolation='nearest')
	# plt.savefig("connectivity.png")

if __name__ == '__main__':
	import sys
	print('dwi_model_and_track, sys.argv: ', sys.argv)
	if len(sys.argv) == 5:
		brain_mask_file = sys.argv[1]
		dwi_data_file = sys.argv[2]
		dwi_bval_file = sys.argv[3]
		dwi_bvec_file = sys.argv[4]
		track_gen_model(brain_mask_file, dwi_data_file, dwi_bval_file, dwi_bvec_file)
	elif len(sys.argv) == 6:
		brain_mask_file = sys.argv[1]
		dwi_data_file = sys.argv[2]
		dwi_bval_file = sys.argv[3]
		dwi_bvec_file = sys.argv[4]
		label_file = sys.argv[5]
		track_gen_model_tutorial(brain_mask_file, dwi_data_file, dwi_bval_file, dwi_bvec_file, label_file)
