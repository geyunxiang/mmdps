"""
This file is used to load an mmdpdb file and output its contents to a csv file
"""
import csv
import datetime
from mmdps.util import loadsave
from mmdps.dms.tables import Person
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class MMDPDatabase:
	def __init__(self, dbFilePath):
		# self.engine = create_engine('sqlite:///../import_changgung/mmdpdb.db')
		self.engine = create_engine('sqlite:///' + dbFilePath)
		self.Session = sessionmaker(bind=self.engine)

	def new_session(self):
		return self.Session()

	def personname_to_id(self, personnames):
		session = self.new_session()
		personIDs = []
		for personname in personnames:
			person = session.query(Person).filter_by(name=personname).one()
			personIDs.append(person.id)
		return personIDs

class TextExporter:
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

if __name__ == '__main__':
	mmdb = MMDPDatabase('I:/mmdpdb.db')
	exp = TextExporter(mmdb, 'E:/Results/exported_mmdp.csv', 'personnames.txt', False)
	exp.run()
	exp = TextExporter(mmdb, 'E:/Results/exported_mmdp_anonymized.csv', 'personnames.txt', True)
	exp.run()
