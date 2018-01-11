'''
Subnet analysis
'''

import os
import csv
import numpy as np
from mmdps import PlotUtils
from mmdps.paraproc import run_in_folder
from matplotlib import cm
import matplotlib.pyplot as plt


class SubNet:
	def __init__(self, rawnet, template, subnetinfo):
		self.subnetinfo = subnetinfo
		self.name = self.subnetinfo.name
		self.ticks = self.subnetinfo.labels
		self.count = len(self.ticks)
		self._calc_net(rawnet, template)
		self.original_template = template

	def _calc_net(self, rawnet, template):
		self.idx = template.ticks_to_indexes(self.ticks)
		self.mat = self._sub_matrix(rawnet, self.idx)

	def get_value_at_tick(self, xtick, ytick):
		if xtick not in self.ticks or ytick not in self.ticks:
			print('xtick %s or ytick %s not in SubNet.' % (xtick, ytick))
			return None
		# given self.mat is a symmetric matrix
		return self.mat[self.ticks.index(xtick), self.ticks.index(ytick)]

	@staticmethod
	def _sub_matrix(mat, idx):
		npidx = np.array(idx)
		return mat[npidx[:, np.newaxis], npidx]

class SubNetReporter:
	def __init__(self, subnet=None):
		self.subnet = subnet

	def set_subnet(self, subnet):
		self.subnet = subnet

	def write_net_csv(self, outpath):
		os.makedirs(os.path.dirname(outpath), exist_ok=True)
		with open(outpath, 'w', newline='') as f:
			writer = csv.writer(f)
			self._write_net_csv_add_ticks(self.subnet.mat, self.subnet.ticks, writer)

	def plot_net(self, title, outpath):
		os.makedirs(os.path.dirname(outpath), exist_ok=True)
		mat = self.subnet.mat
		cmap = cm.coolwarm
		xticks = self.subnet.ticks
		fig = PlotUtils.plot_heatmap(mat, cmap, xticks, valuerange=(-1,1))
		plt.title(title, fontsize=25)
		plt.tick_params(axis='both', labelsize=25)
		fig.savefig(outpath)
		plt.close()

	def plot_bnv(self, title, outpath):
		nodefile = self.subnet.original_template.nodefile.create_new_sub(self.subnet.idx)
		modulars = np.ones(len(self.subnet.idx))
		values = np.mean(np.abs(self.subnet.mat), axis=0)
		nodefile.change_modular(modulars)
		nodefile.change_value(values)
		nodepath = outpath + '.node'
		nodefile.write_node_file(nodepath)
		edgepath = outpath + '.edge'
		np.savetxt(edgepath, self.subnet.mat, delimiter=' ')
		mstr = self._bnv_gen_matlab(nodepath, edgepath, title, outpath)
		run_in_folder.run_matlab_in_folder(os.path.abspath('.'), mstr)
		return
		
	@staticmethod
	def _bnv_gen_matlab(nodepath, edgepath, title, outpath):
		rows = []
		rows.append("nodefile = '{}';".format(nodepath))
		rows.append("edgefile = '{}';".format(edgepath))
		rows.append("desc = '{}';".format(title))
		rows.append("outpath = '{}';".format(outpath))
		#rows.append("bnv_mesh = 'BrainMesh_Ch2withCerebellum.nv';")
		rows.append("bnv_mesh = 'BrainMesh_ICBM152_smoothed.nv';")
		rows.append("bnv_cfg = 'BrainNet_Option_net_coloredge_2.mat';")
		rows.append('draw_brain_net(nodefile, edgefile, desc, outpath, bnv_mesh, bnv_cfg);')
		mstr = ''.join(rows)
		return mstr
	@staticmethod
	def _write_net_csv_add_ticks(mat, ticks, writer):
		writer.writerow(['Ticks', *ticks])
		for i in range(len(ticks)):
			writer.writerow([ticks[i], *mat[i]])

class SubNetInfo:
	def __init__(self, name, conf):
		self.name = name
		self.description = conf['description']
		self.template = conf['template']
		self.labels = conf['labels']

class SubNetGroupInfo:
	def __init__(self, name, conf):
		self.name = name
		self.conf = conf
		self.load_subnets()
	def load_subnets(self):
		self.subnets = {}
		for name, conf in self.conf.items():
			subnet = SubNetInfo(name, conf)
			self.subnets[name] = subnet

def load_subnetgroup(conf):
	return SubNetGroupInfo(conf['name'], conf['subnets'])


if __name__ == '__main__':
	from mmdps.loadfile import load_json, load_csvmat
	from mmdps import BrainTemplate
	j = load_json('F:/WangYueheng2/Changgeng/shiyuzheng/scripts/subnet_shiyuzheng.json')
	subnetgroup = load_subnetgroup(j)
	rawnet = load_csvmat('F:/WangYueheng2/BOLD/PreprocessedBOLD/chenguwen_20150711/bold_net/brodmann_lr_3/corrcoef.csv')
	template = BrainTemplate.get_template('brodmann_lr_3')

	os.makedirs('testtmp', exist_ok=True)
	netreporter = SubNetReporter()
	for subnetinfo in subnetgroup.subnets.values():
		subnet = SubNet(rawnet, template, subnetinfo)
		print(subnet.ticks)
		print(subnet.mat.shape)
		print(subnet.mat)
		netreporter.set_subnet(subnet)
		netreporter.write_net_csv('testtmp/' + subnet.name + '.csv')
		netreporter.plot_net(subnet.name, 'testtmp/' + subnet.name + '.png')
