"""
This program imports a single person's data from CD to data storage. The steps are as follows:
1. copy dicom files from CD to data storage; requires user input subject name and scanning time
2. convert dicom files to raw nii files;
3. extract usable modalities from raw nii files and store them in file database
4. generate(update) info database
"""
import argparse
import logging
import os
import shutil

from mmdps import rootconfig
from mmdps.dms import converter, importer, dbgen
from mmdps.util import clock

def copy_dicom_from_CD(scan_folder_name):
	try:
		shutil.copytree(rootconfig.dms.CD_dicom_path, os.path.join(rootconfig.dms.folder_dicom, scan_folder_name))
	except FileExistsError as e:
		logging.error('Destination already exists.\n%s' % e)
		exit()
	logging.info('Dicom copied.')

def convert_dicom_to_raw_nii(scan_folder_name):
	ret = converter.convert_dicom_to_nifti(os.path.join(rootconfig.dms.folder_rawnii, scan_folder_name), os.path.join(rootconfig.dms.folder_rawnii, scan_folder_name))
	if ret == 0:
		logging.info('Successfully converted %s' % scan_folder_name)
	else:
		logging.error('Error converting scan %s with return code %d' % (scan_folder_name, ret))

def extract_modalities(scan_folder_name):
	worker = importer.MRIScanImporter(os.path.join(rootconfig.dms.folder_rawnii), os.path.join(rootconfig.dms.folder_mridata), cls_niftigetter = converter.ChanggungNiftiGetter)
	logging.info('Extracting modalities...')
	modalities_coverage = worker.copy_one_nifti(scan_folder_name)
	logging.info('Extracting modalities finished with coverage: %s' % modalities_coverage)
	return modalities_coverage

def update_database(scan_folder_name, modalities_coverage):
	"""
	:param scan_folder_name:
	:param modalities_coverage: a tuple containing bool values (hasT1, hasT2, hasBOLD, has DWI)
	:return: nothing
	"""
	worker = dbgen.DatabaseGenerator()
	worker.insert_mrirow(scan_folder_name, modalities_coverage[0],
	                     modalities_coverage[1], modalities_coverage[2], modalities_coverage[3])

def main():
	logging.basicConfig(filename='import_changgung.log', level=logging.DEBUG)
	logging.info('New Run: {}'.format(clock.now()))

	parser = argparse.ArgumentParser()
	parser.add_argument('--name', help = 'name of the subject.', required = True, default = '')
	parser.add_argument('--date', help = 'scanning date', required = True, default = '')
	args = parser.parse_args()
	subject_name = args.name
	scan_date = args.date
	scan_folder_name = '%s_%s' % (subject_name, scan_date)

	copy_dicom_from_CD(scan_folder_name)
	convert_dicom_to_raw_nii(scan_folder_name)
	modalities_coverage = extract_modalities(scan_folder_name)
	update_database(scan_folder_name, modalities_coverage)

if __name__ == '__main__':
	main()
