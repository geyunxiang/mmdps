"""
Result
"""
import os, glob
import numpy as np
from matplotlib import pyplot as plt

from mmdps import brain_template
from mmdps.loadfile import load_csvmat
from mmdps.utils import plot_utils

# dynamic related
def filter_DFCs(raw_dfcs, template_dfcs):
	"""
	Return list of dfc dicts whose tick appears in template_dfcs.
	Input argument raw_dfcs is a list of dfc dicts.
	Argument template_dfcs is a list of strings, aka tick names
	"""
	ret = []
	for dfcDict in raw_dfcs:
		if dfcDict['ticks'] in template_dfcs:
			ret.append(dfcDict)
	return ret

# heatmap, histogram related plotting

def generate_net_heatmap(net, output_file, title):
	fig = plot_utils.plot_heatmap_from_net(net, title)
	os.makedirs(os.path.dirname(output_file), exist_ok = True)
	plt.savefig(output_file)
	plt.close()

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
			ret.append(load_csvmat(os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name)))
		except FileNotFoundError:
			print('File %s not found.' % os.path.join(boldPath, scan, 'bold_net/%s/corrcoef.csv' % template_name))
	return ret

def loadAllNets(boldPath, dynamicIncluded = False, template_name = 'brodmann_lr_3'):
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

def getAllFCAtTick(xtick, ytick, template_name, boldPath = None, all_nets = None, dynamicIncluded = False):
	template = brain_template.get_template(template_name)
	xtickIdx, ytickIdx = template.ticks_to_indexes([xtick, ytick])
	if boldPath is not None:
		return [rawnet[xtickIdx, ytickIdx] for rawnet in loadAllNets(boldPath, dynamicIncluded)]
	if all_nets is not None:
		return [rawnet[xtickIdx, ytickIdx] for rawnet in all_nets]
	raise

def plot_FCHist_at_tick(xtick, ytick, boldPath, template_name, saveDir = None, show_img = False):
	data = getAllFCAtTick(xtick, ytick, boldPath, template_name)
	plt.hist(data, bins = 40, range = (-1, 1))
	plt.xlabel('functional connectivity')
	plt.ylabel('num')
	plt.title('fc hist %s-%s' % (xtick, ytick))
	if saveDir:
		os.makedirs(saveDir, exist_ok = True)
		plt.savefig(os.path.join(saveDir, '%s-%s fc hist.png' % (xtick, ytick)))
	if show_img:
		plt.show()
	else:
		plt.close()

def overlap_FCHists_at_tick(xtick, ytick, dataDict, dynamicIncluded = False, normalize = False, saveDir = None, show_img = False):
	"""
	dataDict should be: {'Beijing':{'path':'/path/to/folder', 'template_name'}} or {'Beijing': {'net_list':[<rawnet1>, <rawnet2>, ...], 'template_name'}}
	The return value, n, is a list of lists. Each list contains the height of each bin. One can calculate the intersection by selecting the minimal value among lists.
	"""
	alpha_value = 1.0/len(dataDict)
	heights = []
	for name, dataValue in dataDict.items():
		if 'path' in dataValue:
			data = getAllFCAtTick(xtick, ytick, dataValue['template_name'], boldPath = dataValue['path'], dynamicIncluded = dynamicIncluded)
		else:
			data = getAllFCAtTick(xtick, ytick, dataValue['template_name'], all_nets = dataValue['net_list'])
		n, bins, patches = plt.hist(data, bins = 25, range = (-1, 1), alpha = alpha_value, label = name, density = normalize)
		heights.append(n)
	plt.legend(loc = 'upper right')
	intersection_area = calculate_intersection_area(heights)
	plt.title('Intersection: %1.3f %s-%s' % (intersection_area, xtick, ytick))
	if saveDir:
		os.makedirs(saveDir, exist_ok = True)
		plt.savefig(os.path.join(saveDir, '%1.3f %s-%s fc hist.png' % (intersection_area, xtick, ytick)))
	if show_img:
		plt.show()
	else:
		plt.close()
	return heights

def calculate_intersection_area(heights):
	"""
	heights is a list of lists.
	Each list contains the height of the bin
	"""
	num_bins = len(heights[0])
	bin_width = 2.0/num_bins
	intersection_area = 0.0
	for bidx in range(num_bins):
		intersection_area += bin_width * min([h[bidx] for h in heights])
	return intersection_area

def intersect_FCHist_at_tick_dynamic_category(xtick, ytick, template_name, dataDict, normalize = False, saveDir = None, show_img = False):
	"""
	Plot the intersection of dynamic functional connections, viewing each window position as a unique category.
	"""
	pass
