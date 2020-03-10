"""
data_customs is the custom of data. 
It is responsible for (mainly) importing and exporting data, 
converting data types and selecting modalities.
The data here refers to MRI dicom and nii files.

The customs only supervises processes up-to the moving of files.
After conversion and moving, the meta-data like patient info 
and scanning date should be registered in mmdpdb

Included converter.py, dicominfo.py, importer.py
"""

import os, subprocess, fnmatch, logging, pydicom, datetime, shutil
from collections import OrderedDict

from mmdps import rootconfig
from mmdps.util import path, loadsave

def parse_date_space_time(s):
	return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def parse_date_only(s):
	return datetime.datetime.strptime(s, '%Y-%m-%d')

def date_only_str(dt):
	return dt.strftime('%Y-%m-%d')

class DicomInfo:
	"""
	Given a loaded dicom file, extract meta-info
	"""
	def __init__(self, dicomfile):
		self.dicomfile = dicomfile
		self.plan = pydicom.read_file(dicomfile)

	def studydate(self):
		thedate = self.plan.StudyDate
		thetime = self.plan.StudyTime
		dt = datetime.datetime.strptime(thedate + ' ' + thetime, '%Y%m%d %H%M%S')
		return str(dt)

	def institution(self):
		return str(self.plan.InstitutionName)

	def manufacturer(self):
		return str(self.plan.Manufacturer)

	def modelname(self):
		return str(self.plan.ManufacturerModelName)

	def patient(self):
		d = OrderedDict()
		try:
			d['ID'] = str(self.plan.PatientID)
		except:
			pass
		try:
			d['NameRaw'] = str(self.plan.PatientName)
		except:
			pass
		try:
			d['Name'] = d['NameRaw'].replace(' ', '').lower()
		except:
			pass
		try:
			d['Birth'] = date_only_str(datetime.datetime.strptime(self.plan.PatientsBirthDate, '%Y%m%d'))
		except:
			pass
		try:
			d['Gender'] = str(self.plan.PatientsSex)
		except:
			pass
		try:
			d['Weight'] = int(self.plan.PatientsWeight)
		except:
			pass
		try:
			d['Age'] = parse_date_space_time(self.studydate()).year - parse_date_only(d['Birth']).year
		except:
			pass
		try:
			d['AgeRaw'] = int(self.plan.PatientsAge[:-1])
		except:
			pass
		return d

	def machine(self):
		d = OrderedDict()
		d['Institution'] = self.institution()
		d['Manufacturer'] = self.manufacturer()
		d['ManufacturerModelName'] = self.modelname()
		return d

	def get_scan_info(self):
		d = OrderedDict()
		d['StudyDate'] = self.studydate()
		d['Machine'] = self.machine()
		d['Patient'] = self.patient()
		return d

	def print_core(self):
		print(self.studydate())
		print(self.institution())
		print(self.manufacturer())
		print(self.modelname())
		print(self.patient())

	def print_all(self):
		print(self.plan)

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
					di = DicomInfo(os.path.join(dirpath, filename))
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

class MRIScanImporter:
	"""
	MRIScan importer. Used to select useful modalities
	"""
	def __init__(self, inMainFolder, outMainFolder, mriscanstxt = None, db_generator=None, cls_niftigetter=NiftiGetter):
		"""
		Import from inMainFolder to outMainFolder, for mriscans from mriscanstxt.
		Update database. Use NiftiGetter class from cls_niftigetter.
		"""
		self.inMainFolder = inMainFolder
		self.outMainFolder = outMainFolder
		if mriscanstxt is not None:
			self.mriscans = loadsave.load_txt(mriscanstxt)
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
		"""
		Deprecated
		Copy all modals for all mriscans.
		"""
		for mriscan in self.mriscans:
			self.copy_one_nifti(mriscan)

	def update_db(self):
		"""
		Deprecated
		Update database
		TODO: better not simply re-generate db.
		"""
		exp = exporter.MRIScanTableExporter(self.outMainFolder, self.db_generator.mritablecsv)
		exp.run()
		self.db_generator.run()

	def run(self):
		"""
		Deprecated
		Run. Copy nifti files and update database.
		"""
		self.copy_nifti()
		self.update_db()
