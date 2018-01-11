'''
Subnet analysis
'''

import os
import csv
import numpy as np
from mmdps.utils import plot_utils
from mmdps.paraproc import run_in_folder
from matplotlib import cm
import matplotlib.pyplot as plt

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
