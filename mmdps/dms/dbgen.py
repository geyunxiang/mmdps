"""Database generator. 

Generate the database using mritable file, motion score file and stroke 
score file, and groups.

Limitation:
Now limited to a sqlite data file.
Updated only when importing DICOM data.

TODO:
Change create_engine to use other RDBMS.
Update existing database when importing other than re-create the database
"""

import csv
import datetime
import os
# from .tables import Base, Person, MRIScan, Group, MotionScore, StrokeScore, MRIMachine
from mmdps.dms.tables import Base, Person, MRIScan, Group, MotionScore, StrokeScore, MRIMachine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from ..util import clock
# from ..util.loadsave import load_txt, load_json
from mmdps.util import clock
from mmdps.util.loadsave import load_txt, load_json
from mmdps import rootconfig

def name_date(mriscan):
	l = mriscan.split('_')
	return l[0], l[1]

class DatabaseGenerator:
	"""Database Generator to update (re-create) the database."""
	def __init__(self, mritablecsv, dbfile='mmdpdb.db', motionscoretablecsv=None,
				 strokescoretablecsv=None, grouptables=None):
		"""Init use various table csv file. will update the mmdpdb.db database by default."""
		self.mritablecsv = mritablecsv
		self.motionscoretablecsv = motionscoretablecsv
		self.strokescoretablecsv = strokescoretablecsv
		self.grouptables = grouptables
		if os.path.isfile(dbfile):
			os.remove(dbfile)
		engine = create_engine('sqlite:///' + dbfile)
		Base.metadata.create_all(engine)
		self.db_people = {}
		self.db_mriscans = {}
		self.db_mrimachines = []
		Session = sessionmaker(bind=engine)
		self.session = Session()

	def parse_scan_datetime(self, s):
		return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

	def build_person(self, name, scaninfo):
		patientdict = scaninfo['Patient']
		patientid = patientdict.get('ID', '')
		gender = patientdict.get('Gender', 'U')
		weight = patientdict.get('Weight', '0')
		if 'Birth' in patientdict:
			birth = datetime.datetime.strptime(patientdict['Birth'], '%Y-%m-%d')
		else:
			ageraw = patientdict.get('AgeRaw', 0)
			scandate = self.parse_scan_datetime(scaninfo['StudyDate'])
			birth = clock.add_years(scandate, -ageraw)
		return Person(name=name, patientid=patientid, gender=gender, weight=weight, birth=birth)

	def add_and_get_mrimachine(self, mrimachinedict):
		for machine in self.db_mrimachines:
			if mrimachinedict['Institution'] == machine.institution and \
			   mrimachinedict['Manufacturer'] == machine.manufacturer and \
			   mrimachinedict['ManufacturerModelName'] == machine.modelname:
				return machine
		machine = MRIMachine(institution=mrimachinedict['Institution'],
							 manufacturer=mrimachinedict['Manufacturer'],
							 modelname=mrimachinedict['ManufacturerModelName'])
		self.db_mrimachines.append(machine)
		return machine

	def insert_mrirow(self, scan, hasT1, hasT2, hasBOLD, hasDWI):
		"""Insert one mriscan record."""
		mrifolder = rootconfig.dms.folder_mridata
		scaninfo = load_json(os.path.join(mrifolder, scan, 'scan_info.json'))
		machine = self.add_and_get_mrimachine(scaninfo['Machine'])
		name, date = name_date(scan)
		dateobj = clock.simple_to_time(date)
		db_mriscan = MRIScan(date=dateobj, hasT1=hasT1, hasT2=hasT2, hasBOLD=hasBOLD, hasDWI=hasDWI)
		machine.mriscans.append(db_mriscan)
		if name not in self.db_people:
			db_person = self.build_person(name, scaninfo)
			self.db_people[name] = db_person
			self.session.add(db_person)
		self.db_people[name].mriscans.append(db_mriscan)

	def insert_mritable(self):
		"""Insert the whole mritable csv file."""
		with open(self.mritablecsv, newline='') as f:
			reader = csv.reader(f)
			next(reader)
			for row in reader:
				scan = row[0]
				hasT1 = bool(int(row[1]))
				hasT2 = bool(int(row[2]))
				hasBOLD = bool(int(row[3]))
				hasDWI = bool(int(row[4]))
				self.insert_mrirow(scan, hasT1, hasT2, hasBOLD, hasDWI)

	def insert_motionscorerow(self, scan, motionscoredict):
		"""Insert one motion score record."""
		name, date = name_date(scan)
		dateobj = clock.simple_to_time(date)
		db_motionscore = MotionScore(date=dateobj, **motionscoredict)
		if name in self.db_people:
			self.db_people[name].motionscores.append(db_motionscore)

	def insert_motionscoretable(self):
		"""Insert the whole motion score records."""
		with open(self.motionscoretablecsv, newline='') as f:
			reader = csv.reader(f)
			next(reader)
			for row in reader:
				scan = row[0]
				TSI = float(row[1])
				Motor = float(row[2])
				Sensory = float(row[3])
				VAS = float(row[4])
				MAS = float(row[5])
				WISCI2 = float(row[6])
				SCIM = float(row[7])
				motionscoredict = {'scTSI': TSI, 'scMotor': Motor, 'scSensory': Sensory, 'scVAS': VAS, 'scMAS': MAS, 'scWISCI2': WISCI2, 'scSCIM': SCIM}
				self.insert_motionscorerow(scan, motionscoredict)

	def insert_strokescorerow(self, scan, strokescoredict):
		"""Insert one stroke score record."""
		name, date = name_date(scan)
		dateobj = clock.simple_to_time(date)
		db_strokescore = StrokeScore(date=dateobj, **strokescoredict)
		if name in self.db_people:
			self.db_people[name].strokescores.append(db_strokescore)

	def insert_strokescoretable(self):
		"""Insert the whole stroke score records."""
		with open(self.strokescoretablecsv, newline='') as f:
			reader = csv.reader(f)
			next(reader)
			for row in reader:
				scan = row[0]
				FMA = float(row[1])
				ARAT = float(row[2])
				WOLF = float(row[3])
				strokescoredict = {'scFMA': FMA, 'scARAT': ARAT, 'scWOLF': WOLF}
				self.insert_strokescorerow(scan, strokescoredict)

	def insert_grouptable(self, grouptable):
		"""Insert one configured group."""
		name, desc, txt = grouptable
		db_group = Group(name=name, description=desc)
		self.session.add(db_group)
		people = load_txt(txt)
		for person in people:
			l = person.split('_')
			personname = l[0]
			if personname in self.db_people:
				db_person = self.db_people[personname]
				db_group.people.append(db_person)

	def insert_grouptables(self):
		"""Insert all groups."""
		for grouptable in self.grouptables:
			self.insert_grouptable(grouptable)

	def run(self):
		"""Run all the insertions."""
		self.insert_mritable()
		if self.motionscoretablecsv:
			self.insert_motionscoretable()
		if self.strokescoretablecsv:
			self.insert_strokescoretable()
		if self.grouptables:
			self.insert_grouptables()
		self.session.commit()
