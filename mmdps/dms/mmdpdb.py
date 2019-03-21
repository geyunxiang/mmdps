"""
This module deals with mmdpdb related actions
"""
from mmdps.dms import tables
from mmdps import rootconfig

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm.exc import MultipleResultsFound

class MMDPDatabase:
	def __init__(self, dbFilePath = rootconfig.dms.mmdpdb_filepath):
		# self.engine = create_engine('sqlite:///../import_changgung/mmdpdb.db')
		self.engine = create_engine('sqlite:///' + dbFilePath)
		self.Session = sessionmaker(bind = self.engine)

	def new_session(self):
		return self.Session()

	def personname_to_id(self, personnames):
		session = self.new_session()
		personIDs = []
		for personname in personnames:
			person = session.query(tables.Person).filter_by(name = personname).one()
			personIDs.append(person.id)
		return personIDs

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
			ret = currentSession.query(exists().where(tables.Person.name == person.name, tables.Person.patientid == person.id))
			if ret is None:
				currentSession.add(person)
		except MultipleResultsFound:
			print('Multiple same person found!')

	# search for new scans
	allNewScans = newSession.query(tables.MRIScan).all()
	for scan in allNewScans:
		try:
			ret = currentSession.query(exists().where(tables.MRIScan.filename == scan.filename))
			if ret is None:
				currentSession.add(scan)
		except MultipleResultsFound:
			print('Multiple same scans found!')
	currentSession.commit()
	currentSession.close()
	newSession.close()
