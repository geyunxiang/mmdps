"""Database sql-alchemy tables.

Define the database by sql-alchemy tables.
Can ease the selection of RDBMS, and much more if use ORM properly.
"""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# table for many to many relationship
association_table_group_person = Table(
	'association_group_person', Base.metadata,
	Column('group_id', Integer, ForeignKey('groups.id')),
	Column('person_id', Integer, ForeignKey('people.id'))
)

association_table_group_mriscan = Table(
	'association_group_mriscan', Base.metadata,
	Column('group_id', Integer, ForeignKey('groups.id')),
	Column('scan_id', Integer, ForeignKey('mriscans.id'))
)

association_table_group_eegscan = Table(
	'association_group_eegscan', Base.metadata,
	Column('group_id', Integer, ForeignKey('groups.id')),
	Column('scan_id', Integer, ForeignKey('eegscans.id'))
)

association_table_group_study = Table(
	'association_group_study', Base.metadata,
	Column('group_id', Integer, ForeignKey('groups.id')),
	Column('study_id', Integer, ForeignKey('researchstudy.id'))
)

class BaseModel(Base):
	"""Base model."""
	__abstract__ = True

class Person(BaseModel):
	"""Person."""
	__tablename__ = 'people'
	#__table_args__ = {"mysql_charset": "utf8"}
	# columns
	id = Column(Integer, primary_key=True)
	patientid = Column(String)
	mriid = Column(String)
	eegid = Column(String)
	datasource = Column(String)
	name = Column(String)
	gender = Column(String)
	birth = Column(DateTime)
	weight = Column(Integer)

	# relationships
	mriscans = relationship('MRIScan', back_populates='person')
	eegscans = relationship('EEGScan', back_populates='person')
	groups = relationship('Group', secondary=association_table_group_person, back_populates='people')

	def __repr__(self):
		return "<Person(name='{}', gender='{}', birth='{}', weight='{}'>".format(self.name, self.gender, self.birth, self.weight)

	@classmethod
	def build_person(cls, name, scaninfo):
		"""
		Used when new person is introduced
		"""
		from mmdps.util import clock
		patient_dict = scaninfo['Patient']
		patientid = patient_dict.get('ID', '')
		gender = patient_dict.get('Gender', 'U')
		weight = patient_dict.get('Weight', '0')
		if 'Birth' in patient_dict:
			birth = datetime.datetime.strptime(patient_dict['Birth'], '%Y-%m-%d')
		else:
			ageraw = patient_dict.get('AgeRaw', 0)
			scandate = datetime.datetime.strptime(scaninfo['StudyDate'], '%Y-%m-%d %H:%M:%S') # parse scan datetime
			birth = clock.add_years(scandate, -ageraw)
		return Person(name = name, patientid = patientid, gender = gender, weight = weight, birth = birth)

class MRIMachine(BaseModel):
	"""MRIMachine."""
	__tablename__ = 'mrimachines'
	# columns
	id = Column(Integer, primary_key=True)
	institution = Column(String)
	manufacturer = Column(String)
	modelname = Column(String)

	# relationships
	mriscans = relationship('MRIScan', back_populates='mrimachine')

	def __repr__(self):
		return "<MRIMachine(institution='{}', manufacturer='{}', modelname='{}'>".format(self.institution, self.manufacturer, self.modelname)

class EEGMachine(BaseModel):
	__tablename__ = 'eegmachines'
	id = Column(Integer, primary_key=True)
	devicename = Column(String)
	devicemode = Column(String)
	recordchannelsettinggroup = Column(String)
	recordmontagename = Column(String)
	recordprotocolname = Column(String)
	recordeegcapname = Column(String)

	# relationships
	eegscans = relationship('EEGScan', back_populates='eegmachine')

class MRIScan(BaseModel):
	"""MRIScan."""
	__tablename__ = 'mriscans'
	# columns
	id = Column(Integer, primary_key=True)
	filename = Column(String)
	person_id = Column(Integer, ForeignKey('people.id'))
	mrimachine_id = Column(Integer, ForeignKey('mrimachines.id'))
	date = Column(DateTime)
	hasT1 = Column(Boolean)
	hasT2 = Column(Boolean)
	hasBOLD = Column(Boolean)
	hasDWI = Column(Boolean)

	# relationships
	person = relationship('Person', back_populates='mriscans')
	mrimachine = relationship('MRIMachine', back_populates='mriscans')
	groups = relationship('Group', secondary = association_table_group_mriscan, back_populates = 'mriscans')

	def __repr__(self):
		return "<MRIScan(person_id='{}', filename='{}', hasT1='{}', hasT2='{}', hasBOLD='{}', hasDWI='{}'>".format(self.person_id, self.filename, self.hasT1, self.hasT2, self.hasBOLD, self.hasDWI)

	def get_folder(self):
		return "{}_{}".format(self.person.name, datetime.datetime.strftime(self.date, '%Y%m%d'))

class EEGScan(BaseModel):

	__tablename__ = 'eegscans'
	#__table_args__ = {"mysql_charset": "utf8"}

	id = Column(Integer, primary_key=True)
	examid = Column(String)
	person_id = Column(Integer, ForeignKey('people.id'))
	eegmachine_id = Column(Integer, ForeignKey('eegmachines.id'))
	date = Column(DateTime)
	examitem = Column(String)
	impedancepos = Column(String)
	impedancedata = Column(String)
	impedanceonline = Column(Boolean)
	begintimestamp = Column(String)
	digitalmin = Column(Integer)
	digitalmax = Column(Integer)
	physicalmin = Column(Float)
	physicalmax = Column(Float)
	samplerate = Column(Integer)

	# relationships
	person = relationship('Person', back_populates='eegscans')
	eegmachine = relationship('EEGMachine', back_populates='eegscans')
	groups = relationship('Group', secondary=association_table_group_eegscan, back_populates='eegscans')

class Group(BaseModel):
	"""Group."""
	__tablename__ = 'groups'
	# columns
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)

	# relationships
	people = relationship('Person', secondary = association_table_group_person, back_populates = 'groups')
	mriscans = relationship('MRIScan', secondary = association_table_group_mriscan, back_populates = 'groups')
	eegscans = relationship('EEGScan', secondary = association_table_group_eegscan, back_populates = 'groups')
	studies = relationship('ResearchStudy', secondary = association_table_group_study, back_populates = 'groups')

	def get_scanlist(self):
		return [scan.filename for scan in self.mriscans]

	def get_subject_namelist(self):
		return [person.name for person in self.people]

	def __repr__(self):
		return "<Group(name='{}', description='{}'>".format(self.name, self.description)

class ResearchStudy(BaseModel):
	"""
	A ResearchStudy stands for a specific research. It includes multiple groups.
	"""
	__tablename__ = 'researchstudy'
	# columns
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	alias = Column(String)

	# relationships
	groups = relationship('Group', secondary = association_table_group_study, back_populates = 'studies')

	def __repr__(self):
		return "<Study(name='{}', description='{}', alias='{}')>".format(self.name, self.description, self.alias)

	def list_group(self):
		res = []
		for gp in self.groups:
			res.append(gp.name)
		return res

	def get_group(self, name_string):
		for gp in self.groups:
			if name_string in gp.name:
				return gp
		return None

	def get_scans_of_subject(self, subject_name):
		scan_list = []
		for gp in self.groups:
			for scan in gp.mriscans:
				if scan.person.name == subject_name:
					scan_list.append(scan)
		scan_list = sorted(scan_list, key = lambda x: x.date)
		return scan_list
