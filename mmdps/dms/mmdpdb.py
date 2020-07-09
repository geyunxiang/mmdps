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
import datetime

from sqlalchemy import create_engine, exists, and_
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from mmdps.proc import atlas
from mmdps.dms import tables
from mmdps.util import loadsave
from mmdps import rootconfig

from mmdps.dms import mongodb_database, redis_database

class MMDPDatabase:
	def __init__(self, data_source = 'Changgung'):
		self.rdb = redis_database.RedisDatabase()
		self.mdb = mongodb_database.MongoDBDatabase(data_source = data_source)
		self.sdb = SQLiteDB()
		self.data_source = data_source

	def get_feature(self, scan_list, atlasobj, feature_name):
		"""
		Designed for static networks and attributes query.
		Using scan name , altasobj/altasobj name, feature name and data source(the default is Changgung) to query data from Redis.
		If the data is not in Redis, try to query data from Mongodb and store the data in Redis.
		If the query succeeds, return a Net or Attr class, if not, rasie an arror.
		"""
		#wrong input check
		return_single = False
		if type(scan_list) is str:
			scan_list = [scan_list]
			return_single = True
		if type(atlasobj) is atlas.Atlas:
			atlasobj = atlasobj.name
		ret_list = []
		for scan in scan_list:
			res = self.rdb.get_static_value(self.data_source, scan, atlasobj, feature_name)
			if res is not None:
				ret_list.append(res)
			else:
				doc = self.mdb.query_static(scan, atlasobj, feature_name)
				if doc.count() != 0:
					ret_list.append(self.rdb.set_value(doc[0],self.data_source))
				else:
					raise mongodb_database.NoRecordFoundException('No such item in redis and mongodb: ' + scan + ' ' + atlasobj + ' ' + feature_name)
					# raise Exception('No such item in redis and mongodb: ' + scan +' '+ atlasobj +' '+ feature_name)
		if return_single:
			return ret_list[0]
		else:
			return ret_list

	def get_dynamic_feature(self, scan_list, atlasobj, feature_name, window_length, step_size):
		"""
		Designed for dynamic networks and attributes query.
		Using scan name , altasobj/altasobj name, feature name, window length, step size and data source(the default is Changgung)
			to query data from Redis.
		If the data is not in Redis, try to query data from Mongodb and store the data in Redis.
		If the query succeeds, return a DynamicNet or DynamicAttr class, if not, rasie an arror.
		"""
		return_single = False
		if type(scan_list) is str:
			scan_list = [scan_list]
			return_single = True
		if type(atlasobj) is atlas.Atlas:
			atlasobj = atlasobj.name
		ret_list = []
		for scan in scan_list:
			res = self.rdb.get_dynamic_value(self.data_source, scan, atlasobj, feature_name, window_length, step_size)
			if res is not None:
				ret_list.append(res)
			else:
				doc = self.mdb.query_dynamic(scan, atlasobj, feature_name, window_length, step_size)
				if doc.count() != 0:
					mat = self.rdb.set_value(doc,self.data_source)
					ret_list.append(mat)
				else:
					raise mongodb_database.NoRecordFoundException('No such item in redis or mongodb: ' + scan + ' ' + atlasobj + ' ' + feature_name + ' ' + str(window_length) + ' ' + str(step_size))
					# raise Exception('No such item in both redis and mongodb: ' + scan +' '+ atlasobj +' '+ feature_name +' '+
					# 			 ' '+ str(window_length) +' '+ str(step_size))
		if return_single:
			return ret_list[0]
		else:
			return ret_list

	def get_temp_feature(self, feature_collection, feature_name):
		pass

	def save_temp_feature(self, feature_collection, feature_name, value):
		pass

	def set_cache_list(self, cache_key, value):
		"""
		Store a list to redis as cache with cache_key
		"""
		self.rdb.set_list_all_cache(cache_key, value)

	def append_cache_list(self, cache_key, value):
		"""
		Append value to a list in redis with cache_key.
		If the given key is empty in redis, a new list will be created.
		"""
		self.rdb.set_list_cache(cache_key, value)

	def get_cache_list(self, cache_key):
		"""
		Return a list with given cache_key in redis
		"""
		return self.rdb.get_list_cache(cache_key)

	def save_cache_list(self, cache_key):
		"""
		Save list from redis to MongoDB
		"""
		a = self.get_cache_list(cache_key)
		self.mdb.put_temp_data(a,cache_key)

	def delete_cache_list(self, cache_key):
		"""
		Remove list from redis and mongo
		"""
		self.rdb.delete_key_cache(cache_key)
		# TODO: delete the list from mongo

	def get_study(self, alias):
		study_list = self.sdb.get_all_studies()
		for study in study_list:
			if study.alias.find(alias) != -1:
				return study

	def get_group(self, group_name):
		group_list = self.sdb.get_all_groups()
		for group in group_list:
			if group.name.find(group_name) != -1:
				return group

	def get_Changgung_HC(self):
		return self.sdb.get_Changgung_HC()


class SQLiteDB:
	"""
	SQLite stores meta-info like patient information, scan date, group 
	relationships, research study cases and so on. 
	"""
	def __init__(self, dbFilePath = rootconfig.dms.mmdpdb_filepath):
		self.engine = create_engine('sqlite:///' + dbFilePath)
		self.Session = sessionmaker(bind = self.engine)
		self.session = self.Session()

	def new_session(self):
		return self.Session()

	def insert_mrirow(self, scan, hasT1, hasT2, hasBOLD, hasDWI, mrifolder = rootconfig.dms.folder_mridata):
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

		# check MRIMachine
		scan_info = loadsave.load_json(os.path.join(mrifolder, scan, 'scan_info.json'))
		ret = self.session.query(exists().where(and_(tables.MRIMachine.institution == scan_info['Machine']['Institution'], tables.MRIMachine.manufacturer == scan_info['Machine']['Manufacturer'], tables.MRIMachine.modelname == scan_info['Machine']['ManufacturerModelName']))).scalar()
		if ret:
			machine = self.session.query(tables.MRIMachine).filter(and_(tables.MRIMachine.institution == scan_info['Machine']['Institution'], tables.MRIMachine.manufacturer == scan_info['Machine']['Manufacturer'], tables.MRIMachine.modelname == scan_info['Machine']['ManufacturerModelName'])).one()
		else:
			# insert new MRIMachine
			machine = tables.MRIMachine(institution = scan_info['Machine']['Institution'],
										manufacturer = scan_info['Machine']['Manufacturer'],
										modelname = scan_info['Machine']['ManufacturerModelName'])

		# check Person
		name = scan_info['Patient']['Name']
		try:
			dateobj = datetime.datetime.strptime(scan_info['StudyDate'], '%Y-%m-%d %H:%M:%S')
		except ValueError:
			dateobj = None
		db_mriscan = tables.MRIScan(date = dateobj, hasT1 = hasT1, hasT2 = hasT2, hasBOLD = hasBOLD, hasDWI = hasDWI, filename = scan)
		machine.mriscans.append(db_mriscan)
		try:
			ret = self.session.query(exists().where(and_(tables.Person.name == name, tables.Person.patientid == scan_info['Patient']['ID']))).scalar()
			if ret:
				person = self.session.query(tables.Person).filter(and_(tables.Person.name == name, tables.Person.patientid == scan_info['Patient']['ID'])).one()
				person.mriscans.append(db_mriscan)
				self.session.add(db_mriscan)
				self.session.commit()
				print('Old patient new scan %s inserted' % scan)
				return 0
		except MultipleResultsFound:
			print('Error when importing: multiple person records found for %s' % name)
			return 2
		db_person = tables.Person.build_person(name, scan_info)
		db_person.mriscans.append(db_mriscan)
		self.session.add(db_person)
		self.session.commit()
		print('New patient new scan %s inserted' % scan)
		return 0

	def get_all_groups(self):
		"""
		Return a list of all groups in this database
		"""
		return self.session.query(tables.Group).all()

	def get_study(self, alias):
		return self.session.query(tables.ResearchStudy).filter_by(alias = alias).one()

	def get_all_studies(self):
		"""
		Return a list of all ResearchStudy in this database
		"""
		return self.session.query(tables.ResearchStudy).all()

	def get_Changgung_HC(self):
		"""
		"""
		return self.session.query(tables.Group).filter_by(name = 'Changgung HC').one()

	def new_group_by_scans(self, group_name, scan_list, desc = None):
		"""
		Initialize a group by a list of scans
		"""
		group = tables.Group(name = group_name, description = desc)
		# check if group already exist
		try:
			self.session.query(tables.Group).filter_by(name = group_name).one()
		except NoResultFound:
			# alright
			for scan in scan_list:
				db_scan = self.session.query(tables.MRIScan).filter_by(filename = scan).one()
				group.scans.append(db_scan)
				group.people.append(db_scan.person)
			self.session.add(group)
			self.session.commit()
			return
		except MultipleResultsFound:
			# more than one record found
			raise Exception("More than one %s group found!" % group_name)
		# found one existing record
		raise Exception("%s group already exist" % group_name)

	def delete_group(self, group_name):
		group_list = self.session.query(tables.Group).filter_by(name = group_name).all()
		# if group is None:
		# 	raise Exception("%s group does not exist!" % group_name)
		for group in group_list:
			self.session.delete(group)
		self.session.commit()

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

	def delete_scan(self, session, mriscanFilename):
		db_scan = session.query(tables.MRIScan).filter_by(filename = mriscanFilename).one()
		session.delete(db_scan)
		session.commit()
