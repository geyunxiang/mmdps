"""Loader is used to load all fusion input.

The fusion input is loaded by loaders.
The loaders are created by fusion constructor. There are config files
to config every loader.
"""
import os
import csv
import json
import numpy as np
# from . import netattr
# from ..util.loadsave import load_csvmat, load_txt
# from ..util import path
from mmdps import rootconfig
from mmdps.proc import netattr
from mmdps.util.loadsave import load_csvmat, load_txt
from mmdps.util import path

class Loader:
	"""Base class Loader is used to load raw array data."""
	def __init__(self, mainfolder, atlasobj):
		"""
		Init the loader.
		- mainfolder: the folder containing all scans
		- csvdict: contains mapping from attr name to file name
		"""
		self.mainfolder = mainfolder
		self.atlasobj = atlasobj
		with open(os.path.join(rootconfig.path.proc, 'attr_dict.json')) as f:
			self.csvdict = json.load(f)
		self.f_preproc = None

	def names(self):
		"""The feature names in csvdict."""
		thenames = []
		for name in self.csvdict:
			thenames.append(name)
		return thenames

	def fullfile(self, mriscan, *p):
		"""Full path for one feature."""
		return os.path.join(self.mainfolder, mriscan, self.atlasobj.name, *p)

	def csvfilename(self, netattrname):
		"""Get the csv filename by feature name."""
		return self.csvdict.get(netattrname, '')

	def loadfilepath(self, mriscan, netattrname):
		"""File path for one feature."""
		return self.fullfile(mriscan, self.csvfilename(netattrname))

	def loaddata(self, mriscan, netattrname):
		"""Load the feature specified by mriscan and feature name.

		Use set_preproc to set a pre-processing function.
		"""
		csvfile = self.loadfilepath(mriscan, netattrname)
		resmat = load_csvmat(csvfile)
		if type(self.f_preproc) is dict:
			if mriscan in self.f_preproc:
				f = self.f_preproc[mriscan]
				if f:
					resmat = f(resmat)
		elif self.f_preproc:
			resmat = self.f_preproc(resmat)
		return resmat

	def load(self, mriscan, netattrname):
		"""Load Mat, with atlasobj."""
		data = self.loaddata(mriscan, netattrname)
		netattrobj = netattr.Mat(data, self.atlasobj, mriscan)
		return netattrobj

	def getshape(self, mriscan, netattrname):
		"""Get data shape."""
		return self.loaddata(mriscan, netattrname).shape

	def set_preproc(self, f_preproc):
		"""Set the pre-process function. A function or mriscan:function dict.
		Will be used when loaddata is called.

		If f_preproc is a function, it will be used like m=f_preproc(m).
		If f_preproc is a dict, it will be used like m=f_preproc[mriscan](m).
		"""
		self.f_preproc = f_preproc

	def loadvstack(self, mriscans, netattrname):
		"""Load all data in every mriscan in mriscans.

		Every feature data for one mriscan is flattened, before vstacked to a matrix.
		"""
		datalist = []
		for mriscan in mriscans:
			currentData = self.loaddata(mriscan, netattrname)
			datalist.append(currentData.flatten())
		datavstack = np.vstack(datalist)
		return datavstack

	def generate_mriscans(self, namelist, num_scan = 1, accumulate = False):
		"""Load specific scans of subjects in namelist. Specify scan number (1st, 2nd, ...)
		namelist is a list of subject names (str)
		Set accumulate = True to load all scans up to (including) num_scan
		"""
		mriscans = []
		lastName = None
		occurrence = 0
		currentScans = []
		for scan in sorted(os.listdir(self.mainfolder)):
			name = scan[:scan.find('_')]
			if name != lastName:
				if lastName in namelist:
					if accumulate:
						mriscans.extend(currentScans[:num_scan])
					else:
						mriscans.append(currentScans[num_scan-1])
				lastName = name
				occurrence = 0
				currentScans = []
			occurrence += 1
			currentScans.append(scan)
		if lastName in namelist:
			if accumulate:
				mriscans.extend(currentScans[:num_scan])
			else:
				mriscans.append(currentScans[num_scan-1])
		# check if some one is missing
		if accumulate and len(mriscans) != num_scan * len(namelist):
			print('Loader Warning: no. mriscans found (%d) not equal to no. subjects (%d) times num_scan (%d)' % (len(mriscans), len(namelist), num_scan))
		elif not accumulate and len(mriscans) != len(namelist):
			print('Loader Warning: no. mriscans found (%d) not equal to no. subjects (%d)' % (len(mriscans), len(namelist)))
		return mriscans

class AttrLoader(Loader):
	"""Attribute loader."""
	def load(self, mriscan, attrname):
		"""
		Load the attribute object, with atlasobj.
		- mriscan: specify which scan to load from
		- attrname: the name of the attr to load
		"""
		attrdata = self.loaddata(mriscan, attrname)
		attr = netattr.Attr(attrdata, self.atlasobj, mriscan)
		return attr

	def loadvstackmulti(self, mriscans, attrnames):
		"""Load all data in every mriscans in mriscans, and every attr in attrnames.

		mriscan0 | attr0v attr1v attr2v
		mriscan1 | attr0v attr1v attr2v
		- mriscans: a list of scans
		- attrnames: a list of names
		The return data dimension is len(mriscans) X (len(attrnames) * atlasobj.count)
		"""
		attrvs = []
		for attrname in attrnames:
			attrv = self.loadvstack(mriscans, attrname)
			attrvs.append(attrv)
		return np.hstack(attrvs)

class NetLoader(Loader):
	"""Net loader."""
	def load(self, mriscan, attrname):
		"""Load the net object, with atlasobj."""
		netdata = self.loaddata(mriscan, attrname)
		net = netattr.Net(netdata, self.atlasobj, mriscan)
		return net

	def loadMulti(self, mriscans, attrname = 'BOLD.net'):
		"""Load a list of nets"""
		ret = []
		for mriscan in mriscans:
			ret.append(self.load(mriscan, attrname))
		return ret

class ScoreLoader:
	"""ScoreLoader is used to load clinical score data."""
	def __init__(self, scoreCsvFile):
		"""
		The loader contains
			- mriscans: a list of scans
			- scoreNames: a list of scoreNames
			- scores_dict[scorename]: a list of actual score values
			- mriscan_scores_dict[mriscan]: a list of all scores related to this scan
		"""
		self.scoreCsvFile = scoreCsvFile
		self.load_scoreCsvFile()

	def load_scoreCsvFile(self):
		"""Load score csv file."""
		if not os.path.isfile(self.scoreCsvFile):
			return
		with open(self.scoreCsvFile, newline='') as f:
			self.mriscan_scores_dict = {}
			self.mriscans = []
			reader = csv.reader(f)
			headers = next(reader)
			self.scoreNames = headers[1:]
			self.scores_dict = {}
			for scorename in self.scoreNames:
				self.scores_dict[scorename] = []
			for row in reader:
				mriscan = row[0]
				self.mriscans.append(mriscan)
				currentScores = [float(s) for s in row[1:]]
				self.mriscan_scores_dict[mriscan] = currentScores
				for iscore, score in enumerate(currentScores):
					self.scores_dict[self.scoreNames[iscore]].append(score)

	def loadvstack(self, mriscans):
		"""Load all scores and vstack them to a matrix for all mriscans, in order."""
		scoresList = []
		for mriscan in mriscans:
			currentScores = self.mriscan_scores_dict[mriscan]
			scoresList.append(currentScores)
		scores_vstack = np.vstack(scoresList)
		return scores_vstack

class GroupLoader:
	"""Group loader is used to load a group."""
	def __init__(self, groupconfigdict):
		"""Init the loader using config dict."""
		self.mriscanstxt = groupconfigdict['txtfile']
		self.load_mriscanstxt()

	def load_mriscanstxt(self):
		"""Load the mriscans txt file."""
		if not os.path.isfile(self.mriscanstxt):
			return
		self.mriscans = load_txt(self.mriscanstxt)
		self.people = self.build_internals(self.mriscans)

	def build_internals(self, mriscans):
		"""Build internals."""
		peopleset = set()
		person_mriscans_dict = {}
		for mriscan in mriscans:
			person, mriscandate = path.name_date(mriscan)
			peopleset.add(person)
			if person in person_mriscans_dict:
				person_mriscans_dict[person].append(mriscan)
			else:
				person_mriscans_dict[person] = [mriscan]
		self.person_mriscans_dict = person_mriscans_dict
		return sorted(list(peopleset))
	
	def person_to_mriscans(self, person):
		"""Person to mriscans, in this group."""
		return self.person_mriscans_dict.get(person, [])

if __name__ == '__main__':
	# test space
	from mmdps.proc import atlas
	atlasobj = atlas.get('brodmann_lr')
	l = AttrLoader('Z:/ChangGungFeatures/', atlasobj)
	print(l.generate_mriscans(['wangzemin'], 1, accumulate = True))
