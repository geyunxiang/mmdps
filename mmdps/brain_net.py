import csv, os, json

import nibabel as nib
import numpy as np

from mmdps import brain_template_old as brain_template
from mmdps import loadfile

class BrainNet:
	"""
	Currently there is only net constructors
	"""
	def __init__(self, net_config_file = None):
		# TODO: one brain net should have only one template
		if net_config_file:
			self.net_config = json.load(open(net_config_file, 'r'))
			self.template = brain_template.get_template(self.net_config['templates'][0])
		else:
			self.template = None
		self.raw_data = None # raw .nii data
		self.net = None
		

	def read_net(self, net_file_path):
		self.net = loadfile.load_csvmat(net_file_path)

	def load_raw_data(self, raw_data_path):
		self.raw_data = nib.load(raw_data_path)

	def generate_brain_net(self, raw_data_path, output_path):
		if not net_config_file:
			raise
		self.load_raw_data(raw_data_path)
		for template_name in self.net_config['templates']:
			outfolder = os.path.join(output_path, template_name)
			os.makedirs(outfolder, exist_ok = True)
			self.gen_by_templatename(template_name, outfolder)

	def gen_by_templatename(self, template_name, outfolder):
		self.template = brain_template.get_template(template_name)
		time_series = self.gen_timeseries_by_template(self.template)
		np.savetxt(os.path.join(outfolder, 'timeseries.csv'), time_series, delimiter=',')
		time_series_corr = np.corrcoef(time_series)
		self.net = time_series_corr
		np.savetxt(os.path.join(outfolder, 'corrcoef.csv'), time_series_corr, delimiter=',')

	def gen_timeseries_by_template(self, template):
		template_img = nib.load(template.niipath)
		self.set_positive_affine_x(self.raw_data)
		self.set_positive_affine_x(template_img)
		data = self.raw_data.get_data()
		template_data = template_img.get_data()
		timepoints = data.shape[3]
		timeseries = np.empty((template.count, timepoints))
		for i, region in enumerate(template.regions):
			regiondots = data[template_data == region, :]
			regionts = np.mean(regiondots, axis=0)
			timeseries[i, :] = regionts
		return timeseries

	def set_positive_affine_x(self, img):
		if img.affine[0, 0] < 0:
			aff = img.affine.copy()
			aff[0, 0] = -aff[0, 0]
			aff[0, 3] = -aff[0, 3]
			img.set_sform(aff)
			img.set_qform(aff)
			data = img.get_data()
			np.copyto(data, nib.flip_axis(data, axis=0))

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

class NodeFile:
	def __init__(self, initnode=None):
		nodedata = []
		if initnode:
			with open(initnode, newline='') as f:
				csvcontent = csv.reader(f, delimiter='\t')
				for row in csvcontent:
					nodedata.append(row)
		self.origin_nodedata = nodedata
		self.nodedata = nodedata.copy()
		self.count = len(nodedata)
	def reset(self):
		self.nodedata = self.origin_nodedata.copy()
	def write_node_file(self, fnamenode):
		with open(fnamenode, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerows(self.nodedata)
	def change_column(self, col, colvalue):
		for irow in range(self.count):
			self.nodedata[irow][col] = colvalue[irow]
	def change_modular(self, modular):
		self.change_column(3, modular)
	def change_value(self, value):
		self.change_column(4, value)
	def change_label(self, label):
		self.change_column(5, label)
	def create_new_sub(self, subindexes):
		subnodefile = NodeFile()
		subnodefile.nodedata = sub_list(self.nodedata, subindexes)
		subnodefile.count = len(subindexes)
		return subnodefile

def sub_list(l, idx):
	nl = []
	for i in idx:
		nl.append(l[i])
	return nl

def get_nodefile(name):
	folder_module = os.path.dirname(os.path.abspath(__file__))
	folder_templates = os.path.join(folder_module, '../../../data/templates')
	folder_templates = os.path.abspath(folder_templates)
	nodepath = os.path.join(folder_templates, name)
	if os.path.isfile(nodepath):
		return NodeFile(nodepath)
	if os.path.isfile(name):
		return NodeFile(name)
	return NodeFile()

if __name__ == '__main__':
	nf = get_nodefile('brodmann_lr.node')
