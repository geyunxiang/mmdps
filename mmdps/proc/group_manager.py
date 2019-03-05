"""
Group manager.
Used to manage group name/scan list.
"""
import os
from mmdps.util import loadsave

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
