import csv, os, json, copy

import nibabel as nib
import numpy as np

from mmdps import brain_template
from mmdps import loadfile

class BrainNet:
	"""
	A brain net must have a template
	"""
	def __init__(self, net_config = None, net = None, template = None):
		self.net_config = net_config
		if self.net_config:
			self.template = brain_template.get_template(self.net_config['template'])
			self.ticks = self.template.ticks
		elif template:
			self.template = template
			self.ticks = self.template.ticks
		else:
			self.template = None
			self.ticks = None
		if net is None:
			self.net = None
		else:
			self.net = net
		self.raw_data = None # raw .nii data

	def get_value_at_tick(self, xtick, ytick):
		if xtick not in self.ticks or ytick not in self.ticks:
			print('xtick %s or ytick %s not in SubNet.' % (xtick, ytick))
			return None
		# given self.mat is a symmetric matrix
		return self.net[self.ticks.index(xtick), self.ticks.index(ytick)]

	def average_net(self, num_to_average):
		self.net /= float(num_to_average)

	def add_net(self, net_file_path):
		if self.net is None:
			self.read_net(net_file_path)
		else:
			self.net += loadfile.load_csvmat(net_file_path)

	def read_net(self, net_file_path):
		self.net = loadfile.load_csvmat(net_file_path)

	def load_raw_data(self, raw_data_path):
		self.raw_data = nib.load(raw_data_path)

	def save_timeseries(self, output_path):
		outfolder = os.path.join(output_path, self.template.name)
		os.makedirs(outfolder, exist_ok = True)
		np.savetxt(os.path.join(outfolder, 'timeseries.csv'), self.time_series, delimiter=',')

	def save_net(self, output_path):
		outfolder = os.path.join(output_path, self.template.name)
		os.makedirs(outfolder, exist_ok = True)
		np.savetxt(os.path.join(outfolder, 'corrcoef.csv'), self.net, delimiter=',')

	def generate_net_by_template(self, raw_data_path):
		self.load_raw_data(raw_data_path)
		self.time_series = self.generate_ROI_time_series()
		self.net = np.corrcoef(self.time_series)

	def generate_ROI_time_series(self):
		template_img = nib.load(self.template.nii_path)
		self.set_positive_affine_x(self.raw_data)
		self.set_positive_affine_x(template_img)
		data = self.raw_data.get_data()
		template_data = template_img.get_data()
		timepoints = data.shape[3]
		timeseries = np.empty((self.template.count, timepoints))
		for i, region in enumerate(self.template.regions):
			regiondots = data[template_data == region, :]
			regionts = np.mean(regiondots, axis=0)
			timeseries[i, :] = regionts
		return timeseries

	def set_positive_affine_x(self, img):
		# TODO: check this
		if img.affine[0, 0] < 0:
			aff = img.affine.copy()
			aff[0, 0] = -aff[0, 0]
			aff[0, 3] = -aff[0, 3]
			img.set_sform(aff)
			img.set_qform(aff)
			data = img.get_data()
			np.copyto(data, nib.flip_axis(data, axis=0))

class SubNet(BrainNet):
	def __init__(self, subnetinfo, parent_net):
		super(SubNet, self).__init__(net = parent_net.net, template = parent_net.template)
		self.subnetinfo = subnetinfo
		self.name = self.subnetinfo.name
		self.ticks = self.subnetinfo.labels
		self.count = len(self.ticks)
		self._calc_net()

	def _calc_net(self):
		self.idx = self.template.ticks_to_indexes(self.ticks)
		self.net = self._sub_matrix(self.net, self.idx)

	@staticmethod
	def _sub_matrix(mat, idx):
		npidx = np.array(idx)
		return mat[npidx[:, np.newaxis], npidx]

class SubNetInfo:
	def __init__(self, name, conf):
		self.name = name # the name of the subnet
		self.description = conf['description']
		self.template = conf['template']
		self.labels = conf['labels'] # a list of ticks

class SubNetGroupInfo:
	def __init__(self, config_file):
		config = json.load(open(config_file, 'r'))
		self.name = config['name']
		self.conf = config['subnets']
		self.load_subnets()

	def load_subnets(self):
		self.subnets = {}
		for name, conf in self.conf.items():
			subnet = SubNetInfo(name, conf)
			self.subnets[name] = subnet

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
