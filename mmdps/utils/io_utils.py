import shutil
import os
import gzip

from mmdps import brain_net

def ungzip(fgz):
	with gzip.open(fgz, 'rb') as fin,\
		 open(fgz[:-3], 'wb') as fout:
		shutil.copyfileobj(fin, fout)

def loadDynamicNetsByCategory(boldPath):
	ret = {}
	for subject in os.listdir(boldPath):
		for netPath in glob.glob(os.path.join(boldPath, subject, 'bold_net/brodmann_lr_3/corrcoef-*')):
			filename = os.path.basename(netPath)
			start = filename[filename.find('-')+1:filename.find('.')]
			end = filename[filename.find('.')+1:filename.rfind('.')]
			if start + '-' + end not in ret:
				ret[start + '-' + end] = [load_csvmat(netPath)]
			else:
				ret[start + '-' + end].append(load_csvmat(netPath))
	return ret

def loadSpecificNets(boldPath, template_name = 'brodmann_lr_3'):
	"""
	This function is used to load the first/second/etc scans of patients
	"""
	ret = []
	subjectName = 'None'
	for scan in sorted(os.listdir(boldPath)):
		if scan.find(subjectName) != -1:
			continue
		subjectName = scan[:scan.find('_')]
		try:
			ret.append(brain_net.BrainNet(net_config = {'template':template_name}, output_path = os.path.join(boldPath, scan, 'bold_net', template_name)))
		except FileNotFoundError:
			print('File %s not found.' % os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name))
	return ret

def loadAllRawNets(boldPath, dynamicIncluded = False, template_name = 'brodmann_lr_3'):
	ret = []
	if dynamicIncluded:
		for scan in os.listdir(boldPath):
			ret += [load_csvmat(filename) for filename in glob.glob(os.path.join(boldPath, scan, 'bold_net/%s/corrcoef*' % template_name))]
	else:
		for scan in os.listdir(boldPath):
			try:
				ret.append(load_csvmat(os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name)))
			except FileNotFoundError:
				print('File %s not found.' % os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name))
	return ret

def loadAllNets(boldPath, template_name = 'brodmann_lr_3'):
	ret = []
	for scan in os.listdir(boldPath):
		try:
			ret.append(brain_net.BrainNet(template = brain_template.get_template(template_name)), output_path = os.path.join(boldPath, scan, 'bold_net', template_name))
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