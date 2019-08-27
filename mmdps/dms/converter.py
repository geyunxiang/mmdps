"""
Converter for dicom and nifti import.

Convert dicom to nifti. 
Get the main modals using NiftiGetter, which is based on globbing.
Inherite NiftiGetter to use with specific converted raw nifti data.
"""

import os
import subprocess
import fnmatch
import logging
import pydicom

from mmdps import rootconfig
from mmdps.util import path, loadsave
from mmdps.dms import dicominfo

def gen_scan_info(infolder, outfolder):
	"""
	Generate scan_info.json file from dicom files.

	Use one random dicom file.
	"""
	found = False
	for dirpath, dirnames, filenames in os.walk(infolder):
		if not found:
			for filename in filenames:
				try:
					pydicom.read_file(os.path.join(dirpath, filename))
					found = True
				except:
					pass
				if found:
					di = dicominfo.DicomInfo(os.path.join(dirpath, filename))
					d = di.get_scan_info()
					scanInfoFile = os.path.join(outfolder, 'scan_info.json')
					loadsave.save_json_ordered(scanInfoFile, d)

def convert_dicom_to_nifti(infolder, outfolder):
	"""
	Convert DICOM to raw NIFTI.
	
	The infolder should be the DICOM folder.
	The outfolder will be the converted NIFTI folder.
	the ret is the conversion program return value. 0 typically indicates success.
	"""
	path.rmtree(outfolder)
	path.makedirs(outfolder)
	gen_scan_info(infolder, outfolder)
	ret = subprocess.call([rootconfig.path.dcm2nii, '-z', 'y', '-o', outfolder, infolder],
		cwd=os.path.dirname(rootconfig.path.dcm2nii))
	print(outfolder, ret)
	return ret

class NiftiGetter:
	"""Get specific modal from converted raw nii files."""
	def __init__(self, niftifolder):
		"""Init with the folder that contains nii files."""
		self.niftifolder = niftifolder
		self._files = os.listdir(self.niftifolder)

	def fnmatch_all(self, pat):
		"""Match all files that match the pattern."""
		res = []
		for file in self._files:
			if fnmatch.fnmatch(file, pat):
				res.append(os.path.join(self.niftifolder, file))
		return res

	def fnmatch_one(self, pat):
		"""Match exactly one file with pattern."""
		res = self.fnmatch_all(pat)
		if len(res) == 1:
			return res[0]
		elif len(res) == 0:
			logging.warning('No file match: {}: {}'.format(pat, self.niftifolder))
			print('No file match:', pat)
			return None
		else:
			logging.warning('More than one match: {} {}: {}'.format(pat, res, self.niftifolder))
			print('More than one match:', pat, res)
			return None

	def get_T1(self):
		"""Get T1 NIFTI file path."""
		return self.fnmatch_one('*T1*.nii.gz')

	def get_T2(self):
		"""Get T2 NIFTI file path."""
		return self.fnmatch_one('*T2*.nii.gz')

	def get_BOLD(self):
		"""Get BOLD NIFTI file path."""
		return self.fnmatch_one('*BOLD*.nii.gz')

	def get_DWI(self):
		"""Get DWI NIFTI file, bval file and bvec file, in a tuple.
		
		Validate with all(dwifiles) == True
		"""
		nii = self.fnmatch_one('*DWI*.nii.gz')
		bval = self.fnmatch_one('*DWI*.bval')
		bvec = self.fnmatch_one('*DWI*.bvec')
		return (nii, bval, bvec)

	def get_ScanInfo(self):
		"""Get scan info dict."""
		return os.path.join(self.niftifolder, 'scan_info.json')

class ChanggungNiftiGetter(NiftiGetter):
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
