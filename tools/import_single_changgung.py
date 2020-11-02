"""
This program imports a single person's data from CD to data storage. The steps are as follows:
1. copy dicom files from CD to data storage; requires user input subject name and scanning time
2. convert dicom files to raw nii files;
3. extract usable modalities from raw nii files and store them in file database
4. generate(update) info database
"""
import argparse
import json
import logging
import os
import shutil

from mmdps import rootconfig
from mmdps.dms import data_customs, dbgen, mmdpdb
from mmdps.util import clock

def copy_dicom_from_CD(scan_folder_name):
	"""
	copy dicom from CD to local temp folder
	dcm2niix conversion is faster on local
	"""
	try:
		# shutil.make_archive(os.path.join(rootconfig.dms.folder_dicom, scan_folder_name), 'zip', rootconfig.dms.CD_dicom_path)
		# shutil.copytree(rootconfig.dms.CD_dicom_path, os.path.join(rootconfig.dms.folder_temp, 'DICOM'))
		os.system('robocopy /S "{}" "{}"'.format(rootconfig.dms.CD_dicom_path, os.path.join(rootconfig.dms.folder_temp, 'DICOM')))
	except FileExistsError as e:
		logging.error('{} Destination already exists.\n{}'.format(clock.now(), e))
		exit()
	logging.info('{} Dicom copied.'.format(clock.now()))

def compress_dicom(scan_folder_name):
	"""
	compress local dicom folder as a zip and move to NAS
	"""
	logging.info('{} Compressing...'.format(clock.now()))
	shutil.make_archive(os.path.join(rootconfig.dms.folder_temp, scan_folder_name), 'zip', os.path.join(rootconfig.dms.folder_temp, 'DICOM'))
	os.system('robocopy /I "{}" "{}"'.format(os.path.join(rootconfig.dms.folder_temp, '{}.zip'.format(scan_folder_name)), rootconfig.dms.folder_dicom))
	logging.info('{} Compressed'.format(clock.now()))

def convert_dicom_to_raw_nii(scan_folder_name):
	ret = data_customs.convert_dicom_to_nifti(os.path.join(rootconfig.dms.folder_temp, 'DICOM'), os.path.join(rootconfig.dms.folder_temp, 'NII'))
	if ret == 0:
		logging.info('{} Successfully converted {}'.format(clock.now(), scan_folder_name))
	else:
		logging.error('{} Error converting scan {} with return code {}'.format(clock.now(), scan_folder_name, ret))
	with open(os.path.join(rootconfig.dms.folder_temp, 'NII', 'scan_info.json')) as f:
		jsonObject = json.load(f)
		print('Subject ID: %s' % jsonObject['Patient']['ID'])
	try:
		# shutil.copytree(os.path.join(rootconfig.dms.folder_temp, 'NII'), os.path.join(rootconfig.dms.folder_rawnii, scan_folder_name))
		os.system('robocopy /S "{}" "{}"'.format(os.path.join(rootconfig.dms.folder_temp, 'NII'), os.path.join(rootconfig.dms.folder_rawnii, scan_folder_name)))
		# remove temp folder
		os.system('rmdir /S /Q "{}"'.format(rootconfig.dms.folder_temp))
	except FileExistsError as e:
		logging.error('{} Destination already exists.\n{}'.format(clock.now(), e))
		exit()
	except PermissionError as e:
		print('PermissionError')
		print(e)
		logging.error('{} PermissionError.\n{}'.format(clock.now(), e))
		exit()
	logging.info('{} raw nii moved to NAS and temp folder removed'.format(clock.now()))

def extract_modalities(scan_folder_name):
	worker = data_customs.MRIScanImporter(os.path.join(rootconfig.dms.folder_rawnii), os.path.join(rootconfig.dms.folder_mridata), cls_niftigetter = data_customs.ChanggungNiftiGetter)
	logging.info('{} Extracting modalities...'.format(clock.now()))
	modalities_coverage = worker.copy_one_nifti(scan_folder_name)
	logging.info('{} Extracting modalities finished with coverage: {}'.format(clock.now(), modalities_coverage))
	return modalities_coverage

def update_sql_database(scan_folder_name, modalities_coverage):
	"""
	:param scan_folder_name:
	:param modalities_coverage: a tuple containing bool values (hasT1, hasT2, hasBOLD, has DWI)
	:return: nothing
	"""
	sdb = mmdpdb.SQLiteDB()
	sdb.insert_mrirow(scan_folder_name, modalities_coverage[0],
					modalities_coverage[1], modalities_coverage[2], modalities_coverage[3])
	# worker = dbgen.DatabaseGenerator()
	# worker.insert_mrirow(scan_folder_name, modalities_coverage[0],
	#                      modalities_coverage[1], modalities_coverage[2], modalities_coverage[3])

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--name', help = 'name of the subject.', required = True, default = '')
	parser.add_argument('--date', help = 'scanning date', required = True, default = '')
	args = parser.parse_args()
	subject_name = args.name
	scan_date = args.date
	scan_folder_name = '%s_%s' % (subject_name, scan_date)

	logging.basicConfig(filename='import_changgung.log', level=logging.DEBUG)
	logging.info('{} New Run {}'.format(clock.now(), scan_folder_name))

	copy_dicom_from_CD(scan_folder_name)
	compress_dicom(scan_folder_name)
	convert_dicom_to_raw_nii(scan_folder_name)
	modalities_coverage = extract_modalities(scan_folder_name)
	update_sql_database(scan_folder_name, modalities_coverage)

if __name__ == '__main__':
	main()
