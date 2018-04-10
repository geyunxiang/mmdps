import csv, os, json, copy

import nibabel as nib
import numpy as np

from mmdps import brain_template
from mmdps import loadfile

class BrainNet:
	"""
	A brain net must have a template
	"""
	def __init__(self, net_config = None, template = None, net = None, time_series = None, output_path = None, net_file_path = None, time_series_file_path = None, raw_data_path = None):
		"""
		BrainNet initialization method:
		* must provide one of:
			- net_config as a dict
			- template as a BrainTemplate
		* provide one of:
			- net, time_series
			- net_file_path, time_series_file_path
			- output_path
			- raw_data_path
		"""
		self.net_config = net_config
		# get template and ticks
		if self.net_config:
			self.template = brain_template.get_template(self.net_config['template'])
			self.ticks = self.template.ticks
		elif template:
			self.template = template
			self.ticks = self.template.ticks
		else:
			# brain net must have a template
			raise
		# get net and time series
		if net is not None:
			self.net = net
			self.time_series = time_series
		elif output_path is not None:
			self.loadNet(output_path = output_path)
		elif net_file_path is not None:
			self.loadNet(net_file_path = net_file_path, time_series_file_path = time_series_file_path)
		elif raw_data_path is not None:
			self.generate_net_from_raw_data(raw_data_path)
		else:
			# brain net must have one of net/time_series, net/time_series file path or raw_data_path
			raise

	def loadNet(self, output_path = None, net_file_path = None, time_series_file_path = None):
		if output_path:
			self.net = loadfile.load_csvmat(os.path.join(output_path, 'corrcoef.csv'))
			self.time_series = np.loadtxt(os.path.join(output_path, 'time_series.csv'), delimiter = ',')
		else:
			self.net = loadfile.load_csvmat(net_file_path)
			self.time_series = np.loadtxt(time_series_file_path, delimiter = ',')

	def load_raw_data(self, raw_data_path):
		return nib.load(raw_data_path)

	def saveNet(self, output_path):
		outfolder = os.path.join(output_path, self.template.name)
		os.makedirs(outfolder, exist_ok = True)
		np.savetxt(os.path.join(outfolder, 'time_series.csv'), self.time_series, delimiter=',')
		np.savetxt(os.path.join(outfolder, 'corrcoef.csv'), self.net, delimiter=',')

	def generate_net_from_raw_data(self, raw_data_path = None):
		if raw_data_path:
			self.raw_data = self.load_raw_data(raw_data_path)
		self.time_series = self.generate_ROI_time_series()
		self.net = np.corrcoef(self.time_series)

	def generate_ROI_time_series(self):
		template_img = nib.load(self.template.nii_path)
		self.set_positive_affine_x(self.raw_data)
		self.set_positive_affine_x(template_img)
		data = self.raw_data.get_data()
		template_data = template_img.get_data()
		timepoints = data.shape[3]
		time_series = np.empty((self.template.count, timepoints))
		for i, region in enumerate(self.template.regions):
			regiondots = data[template_data == region, :]
			regionts = np.mean(regiondots, axis=0)
			time_series[i, :] = regionts
		return time_series

	def get_value_at_tick(self, xtick, ytick):
		if xtick not in self.ticks or ytick not in self.ticks:
			print('xtick %s or ytick %s not in SubNet.' % (xtick, ytick))
			return None
		# given self.mat is a symmetric matrix
		return self.net[self.ticks.index(xtick), self.ticks.index(ytick)]

	def get_value_at_idx(self, xidx, yidx):
		return self.net[xidx, yidx]

	def average_net(self, num_to_average):
		self.net /= float(num_to_average)

	def add_net(self, net_file_path):
		if self.net is None:
			self.net = self.read_net_from_file(net_file_path)
		else:
			self.net += loadfile.load_csvmat(net_file_path)

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

class DynamicNet(BrainNet):
	def __init__(self, parent_net, step = 3, window_length = 100):
		super(DynamicNet, self).__init__(template = parent_net.template, net = parent_net.net, time_series = parent_net.time_series)
		self.stepSize = step
		self.window_length = window_length
		self.dynamic_nets = []
		self.DFCStrength = None
		self.DFCStability = None

	def load_dynamic_nets(self, load_path):
		self.dynamic_nets = []
		start = 0
		while start + self.window_length <= self.time_series.shape[1]:
			self.dynamic_nets.append(np.loadtxt(os.path.join(load_path, 'corrcoef-%d.%d.csv' % (start, start + self.window_length)), delimiter = ','))
			start += self.stepSize

	def save_dynamic_nets(self, output_path):
		outfolder = os.path.join(output_path, self.template.name)
		os.makedirs(outfolder, exist_ok = True)
		start = 0
		for dnet in self.dynamic_nets:
			np.savetxt(os.path.join(outfolder, 'corrcoef-%d.%d.csv' % (start, start + self.window_length)), dnet, delimiter = ',')
			start += self.stepSize

	def generate_dynamic_nets(self):
		start = 0
		while start + self.window_length <= self.time_series.shape[1]:
			self.dynamic_nets.append(np.corrcoef(self.time_series[:, start:start + self.window_length]))
			start += self.stepSize

	def calculate_DFC_characteristics(self):
		"""
		For stability, the higher, the more stable (maximum equals 1)
		"""
		self.DFCStrength = np.zeros(self.dynamic_nets[0].shape)
		self.DFCStability = np.zeros(self.dynamic_nets[0].shape)
		first = True
		for dnet in self.dynamic_nets:
			self.DFCStrength += dnet
			if first:
				lastNet = dnet
				first = False
			else:
				self.DFCStability += abs(dnet - lastNet)/2.0
				lastNet = dnet
		self.DFCStrength /= float(len(self.dynamic_nets))
		self.DFCStability = 1 - self.DFCStability/(float(len(self.dynamic_nets)) - 1)

	def get_DFC_stable_connections(self, topNum = 30, leastNum = None, stableRange = None):
		"""
		Return a list of dicts sorted by the stability of DFC in descending order.
		The dict contains {'index', 'stability', 'strength', 'ticks'}
		"""
		stability = np.tril(self.DFCStability, -1) # lower triangle without main diagnal
		numZeros = np.count_nonzero(stability == 0)
		increasingIndex = stability.argsort(axis = None)
		if leastNum:
			originIndex = np.unravel_index(increasingIndex[numZeros:numZeros + leastNum], stability.shape)
		elif stableRange:
			sortedIndex = increasingIndex[::-1]
			originIndex = np.unravel_index(sortedIndex[stableRange[0]:stableRange[1]], stability.shape)
		else:
			sortedIndex = increasingIndex[::-1]
			originIndex = np.unravel_index(sortedIndex[:topNum], stability.shape)
		ret = []
		for x, y in zip(originIndex[0], originIndex[1]):
			ret.append({'index':(x.item(0), y.item(0)), 'stability':stability[(x, y)].item(0), 'strength':self.DFCStrength[(x, y)].item(0), 'ticks':'%s-%s' % (self.ticks[x], self.ticks[y])})
		return ret

class SubNet(BrainNet):
	def __init__(self, parent_net, subnetInfo):
		super(SubNet, self).__init__(template = parent_net.template, net = parent_net.net, time_series = parent_net.time_series)
		self.subnetInfo = subnetInfo
		self.name = self.subnetInfo.name
		self.ticks = self.subnetInfo.labels
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
	def __init__(self, name, config):
		self.name = name # the name of the subnet
		self.description = config['description']
		self.template = config['template']
		self.labels = config['labels'] # a list of ticks

class SubNetGroupInfo:
	def __init__(self, config_file):
		config = json.load(open(config_file, 'r'))
		self.groupName = config['name']
		self.subnetConfigs = config['subnets']
		self.load_subnets()

	def load_subnets(self):
		self.subnetsInfo = {}
		for name, config in self.subnetConfigs.items():
			subnet = SubNetInfo(name, config)
			self.subnetsInfo[name] = subnet

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
