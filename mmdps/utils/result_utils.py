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

def get_all_fc_at_ticks(xtick, ytick, boldPath, template_name):
	ret = []
	template = brain_template.get_template(template_name)
	for scan in os.listdir(boldPath):
		matpath = os.path.join(boldPath, scan, 'bold_net/brodmann_lr_3/corrcoef.csv')
		rawnet = load_csvmat(matpath)
		ret.append(rawnet[template.ticks_to_indexes([xtick])[0], template.ticks_to_indexes([ytick])[0]])
	return ret

def plot_FCHist_at_tick(xtick, ytick, boldPath, template_name, save_to_file = None, show_img = False):
	data = get_all_fc_at_ticks(xtick, ytick, boldPath, template_name)
	plt.hist(data, bins = 40, range = (-1, 1))
	plt.xlabel('functional connectivity')
	plt.ylabel('num')
	plt.title('fc hist %s-%s' % (xtick, ytick))
	if save_to_file:
		os.makedirs(os.path.dirname(save_to_file), exist_ok = True)
		plt.savefig(os.path.join(self.resultPath, 'FC Hist/%s-%s fc hist.png' % (xtick, ytick)))
	if show_img:
		plt.show()
	else:
		plt.close()

def overlap_FCHists_at_tick(xtick, ytick, boldPaths, names, template_name, save_to_file = None, show_img = False):
	alpha_value = 1.0/len(boldPaths)
	for boldPath, name in zip(boldPaths, names):
		data = get_all_fc_at_ticks(xtick, ytick, boldPath, template_name)
		plt.hist(data, bins = 40, range = (-1, 1), alpha = alpha_value, label = name)
	plt.legend(loc = 'upper right')
	plt.show()
