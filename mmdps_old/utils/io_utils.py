import shutil
import os
import gzip

from mmdps_old import brain_net

def ungzip(fgz):
	with gzip.open(fgz, 'rb') as fin,\
		 open(fgz[:-3], 'wb') as fout:
		shutil.copyfileobj(fin, fout)

def loadDynamicNets(boldPath):
	"""
	This function is used to load dynamic nets as a list.
	Each element in the list is a dynamic network.
	"""
	ret = []
	for subject in sorted(os.listdir(boldPath)):
		net = brain_net.BrainNet(net_config = {'template': 'brodmann_lr_3'}, output_path = os.path.join(boldPath, subject, 'bold_net', 'brodmann_lr_3'))
		dnet = brain_net.DynamicNet(net)
		dnet.load_dynamic_nets(os.path.join(boldPath, subject, 'bold_net', 'brodmann_lr_3'))
		ret.append(dnet)
	return ret

def loadDynamicRawNets(boldPath):
	"""
	This function is used to load dynamic raw nets as np arrays.
	The return value is a dict with key = timestamp.
	Each value is a list of all matrices at this timestamp.
	"""
	ret = {}
	for subject in sorted(os.listdir(boldPath)):
		for netPath in glob.glob(os.path.join(boldPath, subject, 'bold_net/brodmann_lr_3/corrcoef-*')):
			filename = os.path.basename(netPath)
			start = filename[filename.find('-')+1:filename.find('.')]
			end = filename[filename.find('.')+1:filename.rfind('.')]
			if start + '-' + end not in ret:
				ret[start + '-' + end] = [load_csvmat(netPath)]
			else:
				ret[start + '-' + end].append(load_csvmat(netPath))
	return ret

def loadAllTemporalNets(boldPath, totalTimeCase, template_name = 'brodmann_lr_3', subjectList = None):
	"""
	This function is used to load temporal scans. All person with up
	to totalTimeCase number of scans will be loaded and returned in a dict. 
	The key of the dict is the subject name.
	Each element in the dict is the temporal scans of one person. The data are stored
	as a list of BrainNet.
	"""
	if subjectList is not None:
		# read in subjectList
		with open(subjectList) as f:
			subjectList = []
			for line in f.readlines():
				subjectList.append(line.strip())
	ret = {}
	currentPersonScans = []
	subjectName = 'None'
	lastSubjectName = 'Unknown'
	occurrenceCounter = 0
	for scan in sorted(os.listdir(boldPath)):
		subjectName = scan[:scan.find('_')]
		if subjectList is not None and subjectName not in subjectList:
			continue
		if subjectName != lastSubjectName:
			if occurrenceCounter >= totalTimeCase:
				ret[lastSubjectName] = currentPersonScans[:totalTimeCase]
			occurrenceCounter = 0
			lastSubjectName = subjectName
			currentPersonScans = []
		occurrenceCounter += 1
		currentPersonScans.append(brain_net.BrainNet(net_config = {'template':template_name}, output_path = os.path.join(boldPath, scan, 'bold_net', template_name)))
	return ret

def loadSpecificNets(boldPath, template_name = 'brodmann_lr_3', timeCase = 1, subjectList = None):
	"""
	This function is used to load the first/second/etc scans of patients
	Specify which patients to load as a list of strings in subjectList.
	If no subjectList is given, load all scans.
	"""
	if subjectList is not None:
		# read in subjectList
		with open(subjectList) as f:
			subjectList = []
			for line in f.readlines():
				subjectList.append(line.strip())
	ret = []
	subjectName = 'None'
	lastSubjectName = 'Unknown'
	for scan in sorted(os.listdir(boldPath)):
		if scan.find('_') != -1:
			subjectName = scan[:scan.find('_')]
		else:
			subjectName = scan
		if subjectName != lastSubjectName:
			occurrenceCounter = 0
			lastSubjectName = subjectName
		occurrenceCounter += 1
		if subjectList is not None and subjectName not in subjectList:
			continue
		if occurrenceCounter == timeCase:
			try:
				ret.append(brain_net.BrainNet(net_config = {'template':template_name}, output_path = os.path.join(boldPath, scan, 'bold_net', template_name)))
			except FileNotFoundError as e:
				print('File %s not found.' % os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name))
				print(e)
	return ret

def loadAllRawNets(boldPath, dynamicIncluded = False, template_name = 'brodmann_lr_3'):
	ret = []
	if dynamicIncluded:
		for scan in sorted(os.listdir(boldPath)):
			ret += [load_csvmat(filename) for filename in glob.glob(os.path.join(boldPath, scan, 'bold_net/%s/corrcoef*' % template_name))]
	else:
		for scan in sorted(os.listdir(boldPath)):
			try:
				ret.append(load_csvmat(os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name)))
			except FileNotFoundError:
				print('File %s not found.' % os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name))
	return ret

def loadAllNets(boldPath, template_name = 'brodmann_lr_3', scanList = None):
	if scanList is not None:
		# read in scanList
		with open(scanList) as f:
			scanList = []
			for line in f.readlines():
				scanList.append(line.strip())
	ret = []
	if scanList is None:
		scanList = sorted(os.listdir(boldPath))
	for scan in sorted(os.listdir(boldPath)):
		if scan not in scanList:
			continue
		try:
			ret.append(brain_net.BrainNet(net_config = {'template': template_name}, output_path = os.path.join(boldPath, scan, 'bold_net', template_name)))
		except FileNotFoundError:
			print('File %s not found.' % os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name))
	return ret

def save_matrix_csv_style(mat, filePath):
	xlim = mat.shape[0]
	ylim = mat.shape[1]
	xidx = 0
	with open(filePath, 'w') as f:
		while xidx < xlim:
			yidx = 0
			while yidx < ylim:
				if yidx + 1 < ylim:
					f.write('%f\t' % mat[xidx, yidx])
				elif xidx + 1 < xlim:
					f.write('%f\n' % mat[xidx, yidx])
				else:
					f.write('%f' % mat[xidx, yidx])
				yidx += 1
			xidx += 1