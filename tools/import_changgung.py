import os
import argparse
import logging
from mmdps.dms import converter, importer, dbgen
from mmdps.util.loadsave import load_txt
from mmdps import rootconfig
from mmdps.util import clock

logging.basicConfig(filename = 'import_changgung.log', level = logging.DEBUG)
logging.info('New Run: {}'.format(clock.now()))

def apppath(s):
	return os.path.join(WORKING_FOLDER, s)

class ChanggungNiftiGetter(converter.NiftiGetter):
	def __init__(self, niftifolder):
		super().__init__(niftifolder)

	def get_T1(self):
		return self.fnmatch_one('*OSag_3D_T1BRAVO*.nii.gz')

	def get_T2(self):
		return self.fnmatch_one('*OAx_T2_PROPELLER*.nii.gz')

	def get_BOLD(self):
		return self.fnmatch_one('*BOLD-rest*.nii.gz')

	def get_DWI(self):
		nii = self.fnmatch_one('*DTI_24_Directions*.nii.gz')
		bval = self.fnmatch_one('*DTI_24_Directions*.bval')
		bvec = self.fnmatch_one('*DTI_24_Directions*.bvec')
		dwifiles = (nii, bval, bvec)
		if all(dwifiles):
			return dwifiles
		else:
			return None

class ChanggungConverter:
	def __init__(self, dcmMainFolder, niftiMainFolder, mriscantxt):
		self.dcmMainFolder = dcmMainFolder
		self.niftiMainFolder = niftiMainFolder
		self.mriscans = load_txt(mriscantxt)

	def convert_mriscan(self, mriscan):
		dcmfolder = os.path.join(self.dcmMainFolder, mriscan)
		niftifolder = os.path.join(self.niftiMainFolder, mriscan)
		ret = converter.convert_dicom_to_nifti(dcmfolder, niftifolder)
		return ret

	def run(self):
		for mriscan in self.mriscans:
			ret = self.convert_mriscan(mriscan)
			if ret == 0:
				logging.info('{} convert completed'.format(mriscan))
			else:
				logging.warning('{} convert failed, {}'.format(mriscan, ret))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--mriscanstxt', help='a txt file containing mriscan folder names.', required=True, default='')
	parser.add_argument('--bconvert', help='convert dicom to rawnii or not', default='True')
	args = parser.parse_args()

	mriscanstxt = args.mriscanstxt
	if args.mriscanstxt == '':
		# change this when running without arguments
		mriscanstxt = r'F:\MMDPDatabase\new_data_dicom\changgeng_20180430.txt'

	# perform dcm2nii or not
	bconvert = args.bconvert == 'True'

	print('Running with scan list: %s and convertion switch: %s' % (mriscanstxt, bconvert))

	# Working folder
	WORKING_FOLDER = rootconfig.dms.folder_working
	# DICOM main folder
	indcmMainFolder = rootconfig.dms.folder_dicom
	# Raw NIfTI main folder
	outniftiMainFolder = rootconfig.dms.folder_rawnii
	# MRIData main folder
	outMainFolder = rootconfig.dms.folder_mridata

	if bconvert:
		cvt = ChanggungConverter(indcmMainFolder, outniftiMainFolder, mriscanstxt)
		cvt.run()

	csv_motionscores = None
	csv_strokescores = None
	groupconflist = []

	db_generator = dbgen.DatabaseGenerator(
		apppath('rawtable/ChanggengMRITable.csv'),
		rootconfig.dms.mmdpdb_filepath,
		csv_motionscores,
		csv_strokescores,
		groupconflist
		)
	cls_niftigetter = ChanggungNiftiGetter
	imp = importer.MRIScanImporter(outniftiMainFolder, outMainFolder, mriscanstxt, db_generator, cls_niftigetter)
	imp.run()
