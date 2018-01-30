"""
Result
"""
import os

from matplotlib import pyplot as plt

from mmdps import brain_template
from mmdps.loadfile import load_csvmat
from mmdps.utils import plot_utils

def generate_net_heatmap(net, output_file, title):
	fig = plot_utils.plot_heatmap_from_net(net, title)
	os.makedirs(os.path.dirname(output_file), exist_ok = True)
	plt.savefig(output_file)
	plt.close()

def loadAllNets(boldPath):
	return [load_csvmat(os.path.join(boldPath, scan, 'bold_net/brodmann_lr_3/corrcoef.csv')) for scan in os.listdir(boldPath)]

def getAllFCAtHist(xtick, ytick, template_name, boldPath = None, all_nets = None):
	template = brain_template.get_template(template_name)
	xtickIdx, ytickIdx = template.ticks_to_indexes([xtick, ytick])
	if boldPath is not None:
		return [rawnet[xtickIdx, ytickIdx] for rawnet in loadAllNets(boldPath)]
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

def overlap_FCHists_at_tick(xtick, ytick, template_name, dataDict, normalize = False, saveDir = None, show_img = False):
	"""
	dataDict should be: {'Beijing':'/path/to/folder'} or {'Beijing': [<rawnet1>, <rawnet2>, ...]}
	"""
	alpha_value = 1.0/len(dataDict)
	for name, dataValue in dataDict.items():
		if isinstance(dataValue, str):
			data = getAllFCAtHist(xtick, ytick, template_name, boldPath = dataValue)
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