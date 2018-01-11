"""
Result
"""
import os

from matplotlib import pyplot as plt

from mmdps.loadfile import load_csvmat
from mmdps.utils import plot_utils

def generate_net_heatmap(net, output_file, title):
	fig = plot_utils.plot_heatmap_from_net(net, title)
	os.makedirs(os.path.dirname(output_file), exist_ok = True)
	plt.savefig(output_file)
	plt.close()

class ResultGenerator:
	def __init__(self, boldPath, template, resultPath):
		self.boldPath = boldPath
		self.template = template
		self.resultPath = resultPath # 'E:/Results/Beijing Zang FC Analysis/'

	def get_all_fc_at_ticks(self, xtick, ytick):
		ret = []
		for scan in os.listdir(self.boldPath):
			matpath = os.path.join(self.boldPath, scan, 'bold_net/brodmann_lr_3/corrcoef.csv')
			rawnet = load_csvmat(matpath)
			ret.append(rawnet[self.template.ticks_to_indexes([xtick])[0], self.template.ticks_to_indexes([ytick])[0]])
		return ret

	def plot_FCHist_at_tick(self, xtick, ytick):
		data = self.get_all_fc_at_ticks(xtick, ytick)
		plt.hist(data, bins = 40, range = (-1, 1))
		plt.xlabel('functional connectivity')
		plt.ylabel('num')
		plt.title('fc hist %s-%s' % (xtick, ytick))
		plt.savefig(os.path.join(self.resultPath, 'FC Hist/%s-%s fc hist.png' % (xtick, ytick)))
		plt.show()
