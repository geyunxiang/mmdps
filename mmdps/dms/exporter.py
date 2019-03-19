"""
This module contains database-related exporters
"""

import os
import glob
import csv
import datetime
# from ..util import path
from mmdps.util import path, loadsave
from mmdps.dms.tables import Person

class MRIScanTableExporter:
	"""
	The mriscan table exporter.
	This class is used to scan a root folder with MRI data, and 
	output summaries to a csv file. The summary includes scan names
	and modalities each scan contains. 
	"""
	def __init__(self, mriscansfolder, outcsvname):
		"""Use information from the main mriscan folder, export summary to csv."""
		self.mriscansfolder = mriscansfolder
		self.outcsvname = outcsvname
		path.makedirs_file(self.outcsvname)

	def checkmodals(self, mriscanfolder):
		"""Check the modals, exist or not."""
		hasT1 = os.path.isfile(os.path.join(mriscanfolder, 'T1.nii.gz'))
		hasT2 = os.path.isfile(os.path.join(mriscanfolder, 'T2.nii.gz'))
		hasBOLD = os.path.isfile(os.path.join(mriscanfolder, 'BOLD.nii.gz'))
		hasDWI = os.path.isfile(os.path.join(mriscanfolder, 'DWI.nii.gz'))
		return (hasT1, hasT2, hasBOLD, hasDWI)

	def add_row(self, csvwriter, mriscanfolder):
		"""Add one result row to the csv."""
		modalbools = self.checkmodals(mriscanfolder)
		mriscan = os.path.basename(mriscanfolder)
		row = [mriscan]
		for modal in modalbools:
			if modal:
				row.append(1)
			else:
				row.append(0)
		csvwriter.writerow(row)

	def gen_csv(self):
		"""Generate the csv summary file."""
		mriscanfolders = glob.glob(os.path.join(self.mriscansfolder, '*'))
		mriscanfolders = [f for f in mriscanfolders if os.path.isdir(f)]
		with open(self.outcsvname, 'w', newline='') as f:
			csvwriter = csv.writer(f)
			csvwriter.writerow(['name', 'T1', 'T2', 'BOLD', 'DWI'])
			for mriscanfolder in mriscanfolders:
				self.add_row(csvwriter, mriscanfolder)

	def run(self):
		"""Run the generator."""
		self.gen_csv()

class TextExporter:
	"""
	This class is used to export mmdpdb file to a csv file
	"""
	def __init__(self, mmdb, outcsvname, personnamestxt, anonymize=True):
		self.mmdb = mmdb
		self.outcsvname = outcsvname
		self.anonymize = anonymize
		self.personnames = loadsave.load_txt(personnamestxt)

	def run(self):
		session = self.mmdb.new_session()
		ids = self.mmdb.personname_to_id(self.personnames)
		with open(self.outcsvname, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(['MRIScanID', 'personID', 'PatientID', 'Name', 'Gender', 'Birth', 'Weight', 'Institution', 'Manufacturer', 'ModelName', 'ScanDate', 'HasT1', 'HasT2', 'HasBOLD', 'HasDWI'])
			for personID in ids:
				person = session.query(Person).get(personID)
				birthdate = person.birth.strftime('%Y_%m_%d')
				print(person)
				if self.anonymize:
					personName = 'P{}'.format(person.id)
					patientID = 'hidden'
				else:
					personName = person.name
					patientID = person.patientid
				for mriscan in person.mriscans:
					scandate = datetime.datetime.strftime(mriscan.date, '%Y_%m_%d')
					machine = mriscan.mrimachine
					writer.writerow([mriscan.id, person.id, patientID, personName, person.gender, birthdate, person.weight, machine.institution, machine.manufacturer, machine.modelname, scandate, mriscan.hasT1, mriscan.hasT2, mriscan.hasBOLD, mriscan.hasDWI])
