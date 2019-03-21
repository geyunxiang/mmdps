"""
This module deals with mmdpdb related actions
"""
from mmdps.dms import tables
from mmdps import rootconfig

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
