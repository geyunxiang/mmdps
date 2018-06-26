"""
Result
"""
import os, glob
import numpy as np
from matplotlib import pyplot as plt

from mmdps_old import brain_template, brain_net
from mmdps_old.utils import plot_utils, io_utils

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

def getAllFCAtTick(xtick, ytick, all_nets, dynamicIncluded = False):
	return [net.get_value_at_tick(xtick, ytick) for net in all_nets]

def plot_FCHist_at_tick(xtick, ytick, all_nets = None, template_name = 'brodmann_lr_3', normalize = True, saveDir = None, show_img = False):
	data = getAllFCAtTick(xtick, ytick, all_nets)
	n, bins, patches = plt.hist(data, bins = 25, range = (-1, 1), density = normalize)
	plt.title('fc hist %s-%s' % (xtick, ytick))
	if saveDir:
		os.makedirs(saveDir, exist_ok = True)
		plt.savefig(os.path.join(saveDir, '%s-%s fc hist.png' % (xtick, ytick)))
	if show_img:
		plt.show()
	else:
		plt.close()
	return n

def overlap_FCHists_at_tick(xtick, ytick, dataDict, normalize = False, saveDir = None, show_img = False):
	"""
	dataDict should be: {'Beijing':{'path':'/path/to/folder', 'template_name'}} or {'Beijing': {'net_list':[<rawnet1>, <rawnet2>, ...], 'template_name'}} or {'Beijing':{'value_list':[1, 2, 3, ...]}}
	The return value, n, is a list of lists. Each list contains the height of each bin. One can calculate the intersection by selecting the minimal value among lists.
	"""
	alpha_value = 1.0/len(dataDict)
	heights = []
	for name, dataValue in dataDict.items():
		if 'path' in dataValue:
			data = getAllFCAtTick(xtick, ytick, dataValue['template_name'], boldPath = dataValue['path'], dynamicIncluded = dynamicIncluded)
		elif 'net_list' in dataValue:
			data = getAllFCAtTick(xtick, ytick, dataValue['net_list'])
		else:
			data = dataValue['value_list']
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

def plot_hist_per_subject(subjectName, subjectNet, normalize = False, saveDir = None, show_img = False):
	"""
	This function is used to plot the histogram of all connections for one person. 
	"""
	plt.hist(subjectNet.get_all_connection_values(), bins = 25, range = (-1, 1), label = subjectName, density = normalize)
	plt.title(subjectName)
	if saveDir:
		os.makedirs(saveDir, exist_ok = True)
		plt.savefig(os.path.join(saveDir, '%s fc hist.png' % (subjectName)))
	if show_img:
		plt.show()
	else:
		plt.close()
