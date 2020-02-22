"""
This module deals with mmdpdb related actions.

mmdpdb is the database of MMDPS, containing 3 databased.
	1. SQLite stores meta-info like
	   patient information, scan date, group relationships, 
	   research study cases and so on. 
	2. MongoDB keeps all extracted features like networks
	   and attributes. 
	3. Redis is a high-speed cache that starts up upon request. 
"""
import os

from mmdps.dms import tables
from mmdps.util import loadsave, clock
from mmdps import rootconfig

from sqlalchemy import create_engine, exists, and_
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm.exc import MultipleResultsFound

class MMDPDatabase:
	def __init__(self, dbFilePath = rootconfig.dms.mmdpdb_filepath):
		# self.engine = create_engine('sqlite:///../import_changgung/mmdpdb.db')
		self.engine = create_engine('sqlite:///' + dbFilePath)
		self.Session = sessionmaker(bind = self.engine)
		self.session = self.Session()

	def new_session(self):
		return self.Session()

	def insert_mrirow(self, scan, hasT1, hasT2, hasBOLD, hasDWI):
		"""Insert one mriscan record."""
		# check if scan already exist
		try:
			ret = self.session.query(exists().where(tables.MRIScan.filename == scan)).scalar()
			if ret:
				# record exists
				return 0
		except MultipleResultsFound:
			print('Error when importing: multiple scan records found for %s' % scan)
			return 1
		mrifolder = rootconfig.dms.folder_mridata
		scaninfo = loadsave.load_json(os.path.join(mrifolder, scan, 'scan_info.json'))

		machine = tables.MRIMachine(institution = scaninfo['Machine']['Institution'],
							 manufacturer = scaninfo['Machine']['Manufacturer'],
							 modelname = scaninfo['Machine']['ManufacturerModelName'])

		name, date = scan.split('_')
		dateobj = clock.simple_to_time(date)
		db_mriscan = tables.MRIScan(date = dateobj, hasT1 = hasT1, hasT2 = hasT2, hasBOLD = hasBOLD, hasDWI = hasDWI, filename = scan)
		machine.mriscans.append(db_mriscan)
		try:
			ret = self.session.query(exists().where(and_(tables.Person.name == name, tables.Person.patientid == scaninfo['Patient']['ID']))).scalar()
			if ret:
				self.session.add(db_mriscan)
				person = self.session.query(tables.Person).filter_by(name = name).one()
				person.mriscans.append(db_mriscan)
				self.session.commit()
				print('Old patient new scan %s inserted' % scan)
				return 0
		except MultipleResultsFound:
			print('Error when importing: multiple person records found for %s' % name)
			return 2
		db_person = tables.Person.build_person(name, scaninfo)
		db_person.mriscans.append(db_mriscan)
		self.session.add(db_person)
		self.session.commit()
		print('New patient new scan %s inserted' % scan)
		return 0

	def personname_to_id(self, personnames):
		session = self.new_session()
		personIDs = []
		for personname in personnames:
			person = session.query(tables.Person).filter_by(name = personname).one()
			personIDs.append(person.id)
		return personIDs

	def get_all_scans_of_person(self, person_name):
		session = self.new_session()
		one_person = session.query(tables.Person).filter_by(name = person_name).one()
		return session.query(tables.MRIScan).filter_by(person_id = one_person.id)

	def deleteScan(self, session, mriscanFilename):
		db_scan = session.query(tables.MRIScan).filter_by(filename = mriscanFilename).one()
		session.delete(db_scan)
		session.commit()

def updateDatabase(newDBFilePath, currentDBFilePath = rootconfig.dms.mmdpdb_filepath):
	"""
	This function is used to update people/mriscans in current database
	Usually used after new data are added
	NOT TESTED
	"""
	currentEngine = create_engine('sqlite:///' + currentDBFilePath)
	newEngine = create_engine('sqlite:///' + newDBFilePath)
	currentSession = sessionmaker(bind = currentEngine)()
	newSession = sessionmaker(bind = newEngine)()

	# search for new people
	allNewPeople = newSession.query(tables.Person).all()
	for person in allNewPeople:
		# find if this person is in current session
		try:
			ret = currentSession.query(exists().where(and_(tables.Person.name == person.name, tables.Person.patientid == person.id))).scalar()
			if not ret:
				currentSession.add(person)
		except MultipleResultsFound:
			print('Multiple same person found!')

	# search for new scans
	allNewScans = newSession.query(tables.MRIScan).all()
	for scan in allNewScans:
		try:
			ret = currentSession.query(exists().where(tables.MRIScan.filename == scan.filename)).scalar()
			if not ret:
				currentSession.add(scan)
		except MultipleResultsFound:
			print('Multiple same scans found!')
	currentSession.commit()
	currentSession.close()
	newSession.close()
