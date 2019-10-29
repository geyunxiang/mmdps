"""
Group manager.
Used to manage group name/scan list.
"""
import os

from mmdps.util import loadsave
from mmdps.dms import tables, mmdpdb
import sqlalchemy

class GroupManager:
	"""
	GroupManager
	This class automatically scan folderPath, finds *.txt files and load name/scan list.
	The list should be named conventionally
		- treatment_scanlist-1.txt: a list of the first scan for treatment group.
		- control_namelist.txt: a list of names for control group.
	"""
	def __init__(self, folderPath):
		self.folderPath = folderPath
		self.nameDict = dict() # key = treatment/control, value = list of names
		self.scanDict = dict() # key = treatment1/control2 etc, value = list of scans
		self.scanFolder()

	def scanFolder(self):
		"""
		scan folder to load name/scan list
		"""
		for filename in sorted(os.listdir(self.folderPath)):
			if filename.find('txt') == -1:
				continue
			if filename.find('scan') == -1 and filename.find('name') == -1:
				continue
			if filename.find('name') != -1:
				group = filename.split('_')[0]
				self.nameDict[group] = loadsave.load_txt(os.path.join(self.folderPath, filename))
			elif filename.find('scan') != -1:
				group = filename.split('_')[0]
				timeCase = filename[filename.find('-')+1:filename.find('.txt')]
				self.scanDict[group+timeCase] = loadsave.load_txt(os.path.join(self.folderPath, filename))

	def genNameDictFromScan(self):
		"""
		Generate name dict from scanDict
		"""
		self.nameDict = dict()
		for group, scanList in self.scanDict.items():
			self.nameDict[group] = []
			for scan in scanList:
				self.nameDict[group].append(scan[:scan.find('_')])

	def allScansWithinGroup(self, groupName):
		"""
		This function will return all scans belonging to groupName
		Essentially selecting all entries with keys containing the given key word
		"""
		groupName = groupName.lower()
		ret = []
		for key, value in self.scanDict:
			if key.find(groupName) != -1:
				ret += value
		return ret

class DatabaseGroupManager:
	"""
	This is an implementation of group manager using mmdpdb
	"""
	def __init__(self, db = mmdpdb.MMDPDatabase()):
		self.db = db
		self.session = self.db.new_session()

	def getScansInGroup(self, groupName):
		group = self.session.query(tables.Group).filter_by(name = groupName).one()
		return group.scans

	def getNamesInGroup(self, groupName):
		group = self.session.query(tables.Group).filter_by(name = groupName).one()
		return group.people

	def getAllGroups(self):
		"""
		Return a list of all groups in this database
		"""
		return self.session.query(tables.Group).all()

	def newGroupByScans(self, groupName, scanList, desc = None):
		"""
		Initialize a group by a list of scans
		"""
		group = tables.Group(name = groupName, description = desc)
		# check if group already exist
		try:
			self.session.query(tables.Group).filter_by(name = groupName).one()
		except sqlalchemy.orm.exc.NoResultFound:
			# alright
			for scan in scanList:
				db_scan = self.session.query(tables.MRIScan).filter_by(filename = scan).one()
				group.scans.append(db_scan)
				group.people.append(db_scan.person)
			self.session.add(group)
			self.session.commit()
			return
		except sqlalchemy.orm.exc.MultipleResultsFound:
			# more than one record found
			raise Exception("More than one %s group found!" % groupName)
		# found one existing record
		raise Exception("%s group already exist" % groupName)

	def newGroupByNames(self, groupName, nameList, scanNum, desc = None, accumulateScan = False):
		"""
		Initialize a group by a list of names. The scans are generated automatically. 
		scanNum - which scan (first/second/etc)
		accumulateScan - whether keep former scans in this group
		"""
		group = tables.Group(name = groupName, description = desc)
		try:
			self.session.query(tables.Group).filter_by(name = groupName).one()
		except sqlalchemy.orm.exc.NoResultFound:
			for name in nameList:
				db_person = self.session.query(tables.Person).filter_by(name = name).one()
				group.people.append(db_person)
				if accumulateScan:
					group.scans += sorted(db_person.mriscans, key = lambda x: x.filename)[:scanNum]
				else:
					group.scans.append(sorted(db_person.mriscans, key = lambda x: x.filename)[scanNum - 1])
			self.session.add(group)
			self.session.commit()
			return
		except sqlalchemy.orm.exc.MultipleResultsFound:
			# more than one record found
			raise Exception("More than one %s group found!" % groupName)
		# found one existing record
		raise Exception("%s group already exist" % groupName)

	def newGroupByNamesAndScans(self, groupName, nameList, scanList, desc = None):
		"""
		Initialize a group by giving both name and scans
		"""
		group = tables.Group(name = groupName, description = desc)
		for name in nameList:
			db_person = self.session.query(tables.Person).filter_by(name = name).one()
			group.people.append(db_person)
		for scan in scanList:
			db_scan = self.session.query(tables.MRIScan).filter_by(filename = scan).one()
			group.scans.append(db_scan)
		self.session.add(group)
		self.commit()

	def deleteGroupByName(self, groupName):
		groupList = self.session.query(tables.Group).filter_by(name = groupName).all()
		# if group is None:
		# 	raise Exception("%s group does not exist!" % groupName)
		for group in groupList:
			self.session.delete(group)
		self.session.commit()

def genDefaultScan(loader, manager, totalScanNum = 2):
		"""
		Generate scanDict from nameDict.
		Specify total number of scans related to one person in totalScanNum
		After this function, manager.scanDict will contain <totalScanNum> keys for each group
			the naming of keys follows this rule: <groupName><totalScanNum> (control1 etc)
		loader can be a basic loader
		"""
		for key, value in manager.nameDict.items():
			for scanIdx in range(totalScanNum):
				manager.scanDict[key+'%d' % (scanIdx + 1)] = loader.generate_mriscans(value, num_scan = scanIdx+1)

def getResearchStudy(alias):
	db = mmdpdb.MMDPDatabase()
	session = db.new_session()
	return session.query(tables.ResearchStudy).filter_by(alias = alias).one()
