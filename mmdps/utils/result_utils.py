"""
Result
"""
import os, glob

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

def loadAllNets(boldPath, dynamicIncluded = False):
	if dynamicIncluded:
		ret = []
		for scan in os.listdir(boldPath):
			ret += [load_csvmat(filename) for filename in glob.glob(os.path.join(boldPath, scan, 'bold_net/brodmann_lr_3/corrcoef*'))]
		return ret
	else:
		return [load_csvmat(os.path.join(boldPath, scan, 'bold_net/brodmann_lr_3/corrcoef.csv')) for scan in os.listdir(boldPath)]

def getAllFCAtHist(xtick, ytick, template_name, boldPath = None, all_nets = None, dynamicIncluded = False):
	template = brain_template.get_template(template_name)
	xtickIdx, ytickIdx = template.ticks_to_indexes([xtick, ytick])
	if boldPath is not None:
		return [rawnet[xtickIdx, ytickIdx] for rawnet in loadAllNets(boldPath, dynamicIncluded)]
	if all_nets is not None:
		return [rawnet[xtickIdx, ytickIdx] for rawnet in all_nets]
	raise

def plot_FCHist_at_tick(xtick, ytick, boldPath, template_name, saveDir = None, show_img = False):
	data = getAllFCAtHist(xtick, ytick, boldPath, template_name)
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

def overlap_FCHists_at_tick(xtick, ytick, template_name, dataDict, dynamicIncluded = False, normalize = False, saveDir = None, show_img = False):
	"""
	dataDict should be: {'Beijing':'/path/to/folder'} or {'Beijing': [<rawnet1>, <rawnet2>, ...]}
	"""
	alpha_value = 1.0/len(dataDict)
	for name, dataValue in dataDict.items():
		if isinstance(dataValue, str):
			data = getAllFCAtHist(xtick, ytick, template_name, boldPath = dataValue, dynamicIncluded = dynamicIncluded)
		else:
			data = getAllFCAtHist(xtick, ytick, template_name, all_nets = dataValue)
		plt.hist(data, bins = 25, range = (-1, 1), alpha = alpha_value, label = name, density = normalize)
	plt.legend(loc = 'upper right')
	if saveDir:
		os.makedirs(saveDir, exist_ok = True)
		plt.savefig(os.path.join(saveDir, '%s-%s fc hist.png' % (xtick, ytick)))
	if show_img:
		plt.show()
	else:
		plt.close()

def intersect_FCHist_at_tick_dynamic_category(xtick, ytick, template_name, dataDict, normalize = False, saveDir = None, show_img = False):
	"""
	Plot the intersection of dynamic functional connections, viewing each window position as a unique category.
	"""
	pass
