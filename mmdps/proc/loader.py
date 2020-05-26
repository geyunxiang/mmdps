"""Loader is used to load all fusion input.

The fusion input is loaded by loaders.
The loaders are created by fusion constructor. There are config files
to config every loader.
"""
import os
import csv
import json
import numpy as np

from mmdps import rootconfig
from mmdps.proc import netattr, atlas
from mmdps.util.loadsave import load_csvmat, load_txt, load_csv_to_list
from mmdps.util import path

class Loader:
	"""Base class Loader is used to load raw array data."""
	def __init__(self, atlasobj, mainfolder = rootconfig.path.feature_root):
		"""
		Init the loader.
		- mainfolder: the folder containing all scans
		- attr_config_dict: contains mapping from attr name to file name
		"""
		self.mainfolder = mainfolder
		self.atlasobj = atlasobj
		with open(os.path.join(rootconfig.path.proc, 'attr_dict.json')) as f:
			self.attr_config_dict = json.load(f)
		self.f_preproc = None

	def get_feature_filenames(self):
		"""The feature filenames in attr_config_dict."""
		filenames = []
		for feat in self.attr_config_dict:
			filenames.append(feat['filename'])
		return filenames

	def fullfile(self, mriscan, *p):
		"""Full path for one feature."""
		return os.path.join(self.mainfolder, mriscan, self.atlasobj.name, *p)

	def csvfilename(self, netattrname):
		"""Get the csv filename by feature name."""
		return self.attr_config_dict.get(netattrname).get('filename')

	def loadfilepath(self, mriscan, netattrname, csvfilename = None):
		"""File path for one feature."""
		if csvfilename is not None:
			return self.fullfile(mriscan, csvfilename)
		return self.fullfile(mriscan, self.csvfilename(netattrname))

	def loaddata(self, mriscan, netattrname, csvfilename = None):
		"""
		Load the feature data specified by mriscan and feature name.
		Return a np mat or vec
		Use set_preproc to set a pre-processing function.
		"""
		if csvfilename is not None:
			csvfile = self.loadfilepath(mriscan, netattrname, csvfilename)
		else:
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

	def loadSingle(self, mriscan, netattrname):
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

class AttrLoader(Loader):
	"""Attribute loader."""
	def loadSingle(self, mriscan, attrname, csvfilename = None):
		"""
		Load the attribute object, with atlasobj.
		- mriscan: specify which scan to load from
		- attrname: the name of the attr to load
		- csvfilename: the name of the attr file name. Specify this parameter to override filename
		"""
		if csvfilename is not None:
			attrdata = self.loaddata(mriscan, attrname, csvfilename)
		else:
			attrdata = self.loaddata(mriscan, attrname)
		attr = netattr.Attr(attrdata, self.atlasobj, mriscan, attrname)
		return attr

	def load_multiple_attrs(self, mriscans, attrname, csvfilename = None):
		"""
		Load a list of netattr.Attr for each scan in mriscans
		attrname = 'BOLD.BC' etc...
		:param mriscans:
		:param attrname:
		:param attrname: the name of the attr file name. Specify this parameter to override filename
		:return:
		"""
		attr_list = []
		for mriscan in mriscans:
			if csvfilename is not None:
				attr_list.append(self.loadSingle(mriscan, attrname, csvfilename))
			else:
				attr_list.append(self.loadSingle(mriscan, attrname))
		return attr_list

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
	def loadSingle(self, mriscan, attrname = 'BOLD.net'):
		"""Load the net object, with atlasobj."""
		netdata = self.loaddata(mriscan, attrname)
		net = netattr.Net(netdata, self.atlasobj, mriscan, attrname)
		return net

	def loadMulti(self, mriscans, attrname = 'BOLD.net'):
		"""Load a list of nets"""
		ret = []
		for mriscan in mriscans:
			ret.append(self.loadSingle(mriscan, attrname))
		return ret

class ScoreLoader:
	"""
	ScoreLoader is used to load clinical score data.
	The scoreCsvFile should contain a column named 'Name' that specifies the name of subjects.
	Other columns are considered as clinical scores.
	The loader stores scores in a dict, with key = person name and value = dict of scores
		- person 1 : dict(score1, score2, ...)
	"""
	def __init__(self, scoreCsvFile, name_column = 'Name'):
		self.scoreCsvFile = scoreCsvFile
		self.name_column = name_column
		self.scoreDict = dict()
		self.load_scoreCsvFile()

	def load_scoreCsvFile(self):
		"""Load score csv file."""
		if not os.path.isfile(self.scoreCsvFile):
			return
		scoreCsvList = load_csv_to_list(self.scoreCsvFile)
		for row in scoreCsvList:
			self.scoreDict[row.pop(self.name_column)] = row

	def loadvstack(self, mriscans):
		"""Load all scores and vstack them to a matrix for all mriscans, in order."""
		scoresList = []
		for mriscan in mriscans:
			currentScores = self.mriscan_scores_dict[mriscan]
			scoresList.append(currentScores)
		scores_vstack = np.vstack(scoresList)
		return scores_vstack

	def __getitem__(self, index):
		ret = self.scoreDict[index]
		for key, itm in ret.items():
			try:
				ret[key] = float(ret[key])
			except:
				pass
		return ret

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

def get_BOLD_feature_name():
	with open(os.path.join(rootconfig.path.proc, 'attr_dict.json')) as f:
		attr_config_dict = json.load(f)
		return [attr_config_dict[feat]['feat_name'] for feat in attr_config_dict if feat.find('BOLD') != -1 and feat.find('net') == -1]

def load_attrs(scans, atlasobj, attrname, rootFolder = rootconfig.path.feature_root, csvfilename = None):
	"""
	Load static attrs as a list
	:param rootFolder:
	:param scans:
	:param atlasobj:
	:return:
	"""
	if type(atlasobj) is str:
		atlasobj = atlas.get(atlasobj)
	l = AttrLoader(atlasobj, rootFolder)
	if csvfilename is not None:
		return l.load_multiple_attrs(scans, attrname, csvfilename)
	return l.load_multiple_attrs(scans, attrname)

def load_single_dynamic_attr(scan, atlasobj, attrname, dynamic_conf, rootFolder = rootconfig.path.feature_root):
	"""
	Return a DynamicAttr (attr.data[tickIdx, timeIdx])
	"""
	if type(atlasobj) is str:
		atlasobj = atlas.get(atlasobj)
	window_length = dynamic_conf[0]
	step_size = dynamic_conf[1]
	# fix dynamic attr feature_name issue
	if attrname.find('bc') != -1 or attrname.find('BC') != -1:
		feature_name = 'BOLD.BC'
	elif attrname.find('ccfs') != -1 or attrname.find('CCFS') != -1:
		feature_name = 'BOLD.CCFS'
	elif attrname.find('le') != -1 or attrname.find('LE') != -1:
		feature_name = 'BOLD.LE'
	elif attrname.find('wd') != -1 or attrname.find('WD') != -1:
		feature_name = 'BOLD.WD'
	else:
		raise Exception('Unknown feature_name %s' % attrname)
	dynamic_attr = netattr.DynamicAttr(None, atlasobj, window_length, step_size, scan = scan, feature_name = feature_name)
	start = 0
	dynamic_foler_path = os.path.join(rootFolder, scan, atlasobj.name, 'bold_net_attr', 'dynamic %d %d' % (step_size, window_length))
	while True:
		dynamic_attr_filepath = os.path.join(dynamic_foler_path, '%s-%d.%d.csv' % (attrname, start, start + window_length))
		if os.path.exists(dynamic_attr_filepath):
			dynamic_attr.append_one_slice(load_csvmat(dynamic_attr_filepath))
			start += step_size
		else:
			# print('loaded %d attrs for %s' % (len(ret[scan]), scan))
			break
	return dynamic_attr

def load_dynamic_attr(scans, atlasobj, attrname, dynamic_conf, rootFolder = rootconfig.path.feature_root):
	"""
	Return a list of DynamicAttr (attr.data[tickIdx, timeIdx])
	Newer version of dynamic attr loader.
	:param rootFolder:
	:param scans:
	:param atlasobj:
	:param attrname:
	:param windowLength:
	:param stepSize:
	:return:
	"""
	if type(atlasobj) is str:
		atlasobj = atlas.get(atlasobj)
	ret = []
	for scan in scans:
		ret.append(load_single_dynamic_attr(scan, atlasobj, attrname, dynamic_conf, rootFolder))
	return ret

def load_dynamic_attrs(scans, atlasobj, attrname, dynamic_conf, rootFolder = rootconfig.path.feature_root):
	"""
	Return a dict of lists of Attrs as dynamic attr
	Dynamic features are saved as inter-region_<feature>-<start>.<end>.csv at bold_net_attr/dynamic <stepSize> <windowLength>/ folder
	Specify attrname as 'inter-region_BC' etc.
	"""
	if type(atlasobj) is str:
		atlasobj = atlas.get(atlasobj)
	ret = {}
	windowLength = dynamic_conf[0]
	stepSize = dynamic_conf[1]
	for scan in scans:
		ret[scan] = []
		start = 0
		dynamic_foler_path = os.path.join(rootFolder, scan, atlasobj.name, 'bold_net_attr', 'dynamic %d %d' % (stepSize, windowLength))
		while True:
			dynamic_attr_filepath = os.path.join(dynamic_foler_path, '%s-%d.%d.csv' % (attrname, start, start+windowLength))
			if os.path.exists(dynamic_attr_filepath):
				ret[scan].append(netattr.Attr(load_csvmat(dynamic_attr_filepath), atlasobj, '%d.%d' % (start, start+windowLength)))
				start += stepSize
			else:
				# print('loaded %d attrs for %s' % (len(ret[scan]), scan))
				break
	return ret

def load_single_network(mriscan, atlasobj, mainfolder = rootconfig.path.feature_root):
	"""
	Load a single network
	"""
	if type(atlasobj) is str:
		atlasobj = atlas.get(atlasobj)
	l = NetLoader(atlasobj, mainfolder)
	return l.loadSingle(mriscan)

def load_single_dynamic_network(scan, atlasobj, dynamic_conf, rootFolder = rootconfig.path.feature_root):
	"""
	Return a DynamicNet (net.data[timeIdx, tickIdx, tickIdx])
	"""
	if type(atlasobj) is str:
		atlasobj = atlas.get(atlasobj)
	window_length = dynamic_conf[0]
	step_size = dynamic_conf[1]
	start = 0
	dynamic_foler_path = os.path.join(rootFolder, scan, atlasobj.name, 'bold_net', 'dynamic %d %d' % (step_size, window_length))
	time_slice_count = len(list(os.listdir(dynamic_foler_path))) - 1 # get rid of timeseries.csv
	dynamic_net = netattr.DynamicNet(np.zeros((atlasobj.count, atlasobj.count, time_slice_count)), atlasobj, window_length, step_size, scan = scan, feature_name = 'BOLD.net')
	timeIdx = 0
	while True:
		dynamic_net_filepath = os.path.join(dynamic_foler_path, 'corrcoef-%d.%d.csv' % (start, start+window_length))
		if os.path.exists(dynamic_net_filepath):
			time_slice_net = load_csvmat(dynamic_net_filepath)
			dynamic_net.data[:, :, timeIdx] = time_slice_net
			timeIdx += 1
			start += step_size
		else:
			break
	return dynamic_net

def load_dynamic_networks(scans, atlasobj, dynamic_conf, rootFolder = rootconfig.path.feature_root):
	"""
	This function loads dynamic networks for each scan into a dict
	The key of the dict is the scan name
		value is a list of networks
	Dynamic networks are saved as corrcoef-<start>.<end>.csv at bold_net/dynamic <stepSize> <windowLength>/ folder
	"""
	if type(atlasobj) is str:
		atlasobj = atlas.get(atlasobj)
	ret = {}
	windowLength = dynamic_conf[0]
	stepSize = dynamic_conf[1]
	for scan in scans:
		ret[scan] = []
		start = 0
		dynamic_foler_path = os.path.join(rootFolder, scan, atlasobj.name, 'bold_net', 'dynamic %d %d' % (stepSize, windowLength))
		while True:
			dynamic_net_filepath = os.path.join(dynamic_foler_path, 'corrcoef-%d.%d.csv' % (start, start+windowLength))
			if os.path.exists(dynamic_net_filepath):
				ret[scan].append(netattr.Net(load_csvmat(dynamic_net_filepath), atlasobj, '%d.%d' % (start, start+windowLength)))
				start += stepSize
			else:
				# print('loaded %d nets for %s' % (len(ret[scan]), scan))
				break
	return ret

def generate_mriscans(namelist, root_folder = rootconfig.path.feature_root, num_scan = 1, accumulate = False):
	"""Load specific scans of subjects in namelist. Specify scan number (1st, 2nd, ...)
	namelist is a list of subject names (str)
	Set accumulate = True to load all scans up to (including) num_scan
	"""
	mriscans = []
	lastName = None
	currentScans = []
	for scan in sorted(os.listdir(root_folder)):
		name = scan[:scan.find('_')]
		try:
			if name != lastName:
				if lastName in namelist:
					if accumulate:
						mriscans.extend(currentScans[:num_scan])
					else:
						mriscans.append(currentScans[num_scan-1])
				lastName = name
				currentScans = []
		except IndexError:
			# some one might not have corresponding scans
			print('Loader Warning: Index error')
			lastName = name
			currentScans = []
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