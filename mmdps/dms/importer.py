"""
Import new data to database.

Copy raw nifti files to database and rename with proper file names.
Update database.
"""

import os
import shutil

from mmdps.dms import converter, exporter
from mmdps.util.loadsave import load_txt
from mmdps.util import path

class MRIScanImporter:
	"""MRIScan importer."""
	def __init__(self, inMainFolder, outMainFolder, mriscanstxt, db_generator=None, cls_niftigetter=converter.NiftiGetter):
		"""
		Import from inMainFolder to outMainFolder, for mriscans from mriscanstxt.
		Update database. Use NiftiGetter class from cls_niftigetter.
		"""
		self.inMainFolder = inMainFolder
		self.outMainFolder = outMainFolder
		self.mriscans = load_txt(mriscanstxt)
		self.db_generator = db_generator
		self.cls_niftigetter = cls_niftigetter

	def copy_one_nifti_modal(self, outfolder, get_path_func, newname):
		"""Copy one modal."""
		modal_path = get_path_func()
		if modal_path is None:
			return False
		if type(modal_path) == str:
			shutil.copy2(modal_path, os.path.join(outfolder, newname))
		else:
			for currentFile in modal_path:
				if currentFile[-7:] == '.nii.gz':
					curnewname = newname + '.nii.gz'
				else:
					_, ext = os.path.splitext(currentFile)
					curnewname = newname + ext
				shutil.copy2(currentFile, os.path.join(outfolder, curnewname))
		return True

	def copy_one_nifti(self, mriscan):
		"""Copy all modals for one mriscan."""
		infolder = os.path.join(self.inMainFolder, mriscan)
		outfolder = os.path.join(self.outMainFolder, mriscan)
		path.makedirs(outfolder)
		niftigetter = self.cls_niftigetter(infolder)
		modalities_coverage = [False, False, False, False]
		modalities_coverage[0] = self.copy_one_nifti_modal(outfolder, niftigetter.get_T1, 'T1.nii.gz')
		modalities_coverage[1] = self.copy_one_nifti_modal(outfolder, niftigetter.get_T2, 'T2.nii.gz')
		modalities_coverage[2] = self.copy_one_nifti_modal(outfolder, niftigetter.get_BOLD, 'BOLD.nii.gz')
		modalities_coverage[3] = self.copy_one_nifti_modal(outfolder, niftigetter.get_DWI, 'DWI')
		self.copy_one_nifti_modal(outfolder, niftigetter.get_ScanInfo, 'scan_info.json')
		return modalities_coverage

	def copy_nifti(self):
		"""Copy all modals for all mriscans."""
		for mriscan in self.mriscans:
			self.copy_one_nifti(mriscan)

	def update_db(self):
		"""Update database
		TODO: better not simply re-generate db.
		"""
		exp = exporter.MRIScanTableExporter(self.outMainFolder, self.db_generator.mritablecsv)
		exp.run()
		self.db_generator.run()

	def run(self):
		"""Run. Copy nifti files and update database."""
		self.copy_nifti()
		self.update_db()
