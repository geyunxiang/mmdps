"""
Feature data container.

Net is a network feature.
Attr is an attribute feature.
Both have corresponding atlasobj in them.
You can create sub-net or sub-attr, the atlasobj is also subbed.
"""
import csv, os
import numpy as np
from pathlib import Path
# from ..util import dataop, path
# from ..util.loadsave import save_csvmat, load_csvmat
from mmdps.proc import atlas
from mmdps.util import dataop, path
from mmdps.util.loadsave import save_csvmat, load_csvmat

class Mat:
	"""
	Mat is a general array data of any dimension, with an atlasobj and a name.
	This is the core of Attr, Net, DynamicAttr and DynamicNet
	"""
	def __init__(self, data, atlasobj, scan = None, feature_name = None):
		"""
		Init the mat.
		"""
		self.data = data
		if type(atlasobj) is str:
			self.atlasobj = atlas.get(atlasobj)
		else:
			self.atlasobj = atlasobj
		self.scan = scan
		self.feature_name = feature_name

class Attr(Mat):
	"""
	Attr is an attribute. It is a one dimensional vector.

	The dimension of the vector is atlasobj.count.

	In static context, an Attr represents one kind of attributes of one person, 
	containing single value for multiple brain regions and resulting in a 1-D 
	vector.
	"""
	def __init__(self, data, atlasobj, scan = None, feature_name = None):
		"""
		Init the attr, using data, atlasobj, and scan.

		The scan can be any string that can be useful.
		"""
		super().__init__(data, atlasobj, scan, feature_name)

	def copy(self):
		"""Copy the attr."""
		newattr = Attr(self.data.copy(), self.atlasobj, self.scan, self.feature_name)
		return newattr

	def gensub(self, subatlasname, subindexes):
		"""Generate a sub, with proper atlasobj."""
		subdata = dataop.sub_vec(self.data, subindexes)
		subatlasobj = self.atlasobj.create_sub(subatlasname, subindexes)
		return Attr(subdata, subatlasobj, self.name)

	def save(self, outfile, addticks=True):
		"""Save the attr, can add ticks defined in atlasobj."""
		if addticks is False:
			save_csvmat(outfile, self.data)
		else:
			path.makedirs_file(outfile)
			with open(outfile, 'w', newline='') as f:
				writer = csv.writer(f)
				writer.writerow(('Region', 'Value'))
				for tick, value in zip(self.atlasobj.ticks, self.data):
					writer.writerow((tick, value))

	def normalize(self):
		if np.max(self.data) < 1.1:
			# already normalized
			return
		for idx in range(self.data.shape[0]):
			self.data[idx] = normalize_feature(self.data[idx], self.name, self.atlasobj)

	def extract_node_community(self):
		"""
		Using Ziliang's program, the inter-region community is saved in a csv file.
		Community is calculated using Louvein algorithm recursively. 
		This function takes the first-level community (each node is associated with a community)
		TODO: the first-level community order might be different in AAL (left-right-interleaved)
		"""
		origin = self.data[:self.atlasobj.count, 1].astype(int)
		new = origin.copy()
		community_counter = 0
		processed_original_community = []
		for idx in range(self.atlasobj.count):
			if origin[idx] in processed_original_community:
				continue
			new[origin == origin[idx]] = community_counter
			community_counter += 1
			processed_original_community.append(origin[idx])
		self.data = new

class DynamicAttr(Mat):
	"""
	DynamicAttr is the dynamic version of Attr.

	In dynamic context, a DynamicAttr represents one kind of dynamic attributes 
	of one person, containing multiple values for multiple brain regions and 
	resulting in a 2-D matrix. (num_regions X num_time_points)
	"""
	def __init__(self, data, atlasobj, window_length, step_size, scan = None, feature_name = None):
		super().__init__(data, atlasobj, scan, feature_name)
		self.window_length = window_length
		self.step_size = step_size

	def normalize(self):
		if np.max(self.data) < 1.1:
			# already normalized
			return
		for xidx in range(self.data.shape[0]):
			for yidx in range(self.data.shape[1]):
				self.data[xidx, yidx] = normalize_feature(self.data[xidx, yidx], self.feature_name, self.atlasobj)

	def append_one_slice(self, data):
		"""
		This function appends one slice of attributes to current dynamic attributes.
		The appended slice should align with current data, or be used to create original data.
		:param data: a np (n,) array
		:return: nothing
		"""
		data = np.reshape(data, (data.shape[0], 1))
		if self.data is None:
			self.data = data
		else:
			self.data = np.concatenate((self.data, data), axis = 1)

	def get_dynamic_at_tick(self, tick):
		tickIdx = self.atlasobj.ticks.index(tick)
		return self.data[tickIdx, :]

class Connection:
	"""
	Connection represents a link/edge in a network.
	It contains xidx, yidx, xtick, ytick in atlasobj, and value
	During initialization, only need to provide x, y, and value
	Connection will judge the datatype of x, y to assign them to 
	idx or ticks.
	"""
	def __init__(self, atlasobj, x, y, value = 0, directional = False):
		self.atlasobj = atlasobj
		if type(x) is str and type(y) is str:
			# tick input
			self.xtick = x
			self.ytick = y
			self.xidx = atlasobj.ticks.index(x)
			self.yidx = atlasobj.ticks.index(y)
		elif type(x) is int and type(y) is int:
			# idx input
			self.xidx = x
			self.yidx = y
			self.xtick = atlasobj.ticks[x]
			self.ytick = atlasobj.ticks[y]
		else:
			raise ValueError('Input tick as str or idx as int during Connection construction')
		self.value = value
		self.directional = directional

	def invert(self):
		"""
		invert the direction. Swap x and y
		"""
		return Connection(self.atlasobj, self.yidx, self.xidx, self.value, self.directional)

	def __str__(self):
		if self.directional:
			line = '%s-%s directional val = %1.3f' % (self.xtick, self.ytick, self.value)
		else:
			line = '%s-%s val = %1.3f' % (self.xtick, self.ytick, self.value)
		return line

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False
		if self.directional and self.xidx == other.xidx and self.yidx == other.yidx:
			return True
		elif not self.directional and self.xidx == other.xidx and self.yidx == other.yidx:
			return True
		elif not self.directional and self.xidx == other.yidx and self.yidx == other.xidx:
			return True
		return False

class Net(Mat):
	"""
	Net is a network. It is a two dimensional sqaure symmetric matrix.

	The dimension of the matrix is (atlasobj.count, atlasobj.count).
	"""
	def __init__(self, data, atlasobj, scan = None, feature_name = 'BOLD.net'):
		"""
		Init the net, using data, atlasobj, and scan.

		The scan can be any string that can be useful.
		""" 
		super().__init__(data, atlasobj, scan, feature_name)

	def rescale_data(self):
		"""
		Re-scale data to valuerange (-1, 1)
		"""
		max_value = np.max(self.data)
		min_value = np.abs(np.min(self.data))
		self.data[self.data>0] /= max_value
		self.data[self.data<0] /= min_value

	def iterate(self):
		"""
		Iterate over all connection in this network
		"""
		for xidx in range(self.atlasobj.count):
			for yidx in range(xidx + 1, self.atlasobj.count):
				yield Connection(self.atlasobj, xidx, yidx, self.data[xidx, yidx])

	def uniqueValueAsList(self, selectedAreas = None):
		"""
		This function takes the strict lower triangle areas of data and convert
		to an np.array. The elements are selected column-wise, without main diag
		Specify selectedAreas to return connections within those areas
		"""
		if selectedAreas is None:
			selectedAreas = self.atlasobj.ticks
		n = self.data.shape[0]
		ret = np.zeros((1, int(n*(n-1)/2)))
		counter = 0
		for colIdx in range(n):
			if self.atlasobj.ticks[colIdx] not in selectedAreas:
				continue
			for rowIdx in range(colIdx + 1, n):
				if self.atlasobj.ticks[rowIdx] not in selectedAreas:
					continue
				ret[0, counter] = self.data[rowIdx, colIdx]
				counter += 1
		return ret

	def setDataFromList(self, valueList):
		"""
		This function takes a list of values and store them in a symmetric matrix
		The matrix is filled column-first
		The input valueList is assumed to be a one-dimensional list
		"""
		n = self.atlasobj.count
		self.data = np.zeros((n, n))
		counter = 0
		for colIdx in range(n):
			for rowIdx in range(colIdx + 1, n):
				self.data[rowIdx, colIdx] = valueList[counter]
				counter += 1
		self.data += np.transpose(self.data)
		self.data += np.eye(n)

	def set_data_from_connections(self, conn_list, unified_value = None):
		"""
		This function takes a list of Connections and store them in a symmetric matrix
		Specify unified_value to override connection value
		"""
		for conn in conn_list:
			if unified_value is not None:
				self.data[conn.xidx, conn.yidx] = unified_value
				self.data[conn.yidx, conn.xidx] = unified_value
			else:
				self.data[conn.xidx, conn.yidx] = conn.value
				self.data[conn.yidx, conn.xidx] = conn.value

	def copy(self):
		"""Copy the net."""
		newnet = Net(self.data.copy(), self.atlasobj, self.name)
		return newnet

	def copySubnetOnly(self, subAreaList):
		"""
		Return a copy of current network, but only values associated
		with the subnetwork specified by areas in the subAreaList argument
		"""
		newnet = Net(self.data.copy(), self.atlasobj, self.scan)
		mask = np.zeros(self.data.shape)
		indexList = [self.atlasobj.ticks.index(area) for area in subAreaList]
		for xidx in range(self.atlasobj.count):
			for yidx in range(self.atlasobj.count):
				if xidx in indexList and yidx in indexList:
					mask[xidx, yidx] = 1
		newnet.data = np.multiply(self.data, mask)
		return newnet

	def gensub(self, subatlasname, subindexes):
		"""Generate a sub net, with proper atlasobj."""
		subdata = dataop.sub_mat(self.data, subindexes)
		subatlasobj = self.atlasobj.create_sub(subatlasname, subindexes)
		return Net(subdata, subatlasobj, self.name)

	def save(self, outfile, addticks=True):
		"""Save the net, can add ticks defined in atlasobj."""
		if addticks is False:
			save_csvmat(outfile, self.data)
		else:
			path.makedirs_file(outfile)
			with open(outfile, 'w', newline='') as f:
				writer = csv.writer(f)
				ticks = self.atlasobj.ticks
				firstrow = ['Region']
				firstrow.extend(ticks)
				writer.writerow(firstrow)
				for tick, datarow in zip(self.atlasobj.ticks, self.data):
					currow = [tick]
					currow.extend(datarow)
					writer.writerow(currow)

	def threshold(self, threshold):
		"""
		Return a copy of current network, with values thresholded
		abs(FC) < threshold --> FC = 0
		"""
		newnet = Net(self.data.copy(), self.atlasobj, self.scan)
		for xidx in range(self.atlasobj.count):
			for yidx in range(self.atlasobj.count):
				if abs(self.data[xidx, yidx]) < threshold:
					newnet.data[xidx, yidx] = 0
		return newnet

	def binarize(self, threshold):
		"""
		Return a copy of current network, with values binarized
		abs(FC) < threshold --> FC = 0
		abs(FC) >= threshold --> FC = 1
		"""
		newnet = Net(self.data.copy(), self.atlasobj, self.scan, self.feature_name)
		newnet.data = (np.abs(newnet.data) >= threshold).astype(int)
		return newnet

	def select_ROI(self, roi_list):
		"""
		Return a copy of current network, with connections associated with regions in 
		roi_list alone.
		roi_list should be of length atlasobj.count with True or False in it.
		Input lists of region ticks or region indices is also accepted.
		"""
		if len(roi_list) != self.atlasobj.count and type(roi_list[0]) is str:
			# list of region ticks
			tmp_list = np.zeros(self.atlasobj.count)
			tmp_list[self.atlasobj.ticks_to_indexes(roi_list)] = 1
			roi_list = tmp_list.astype(bool)
		elif type(roi_list[0]) is int:
			# list of region indices
			tmp_list = np.zeros(self.atlasobj.count)
			tmp_list[roi_list] = 1
			roi_list = tmp_list.astype(bool)
		newnet = Net(self.data.copy(), self.atlasobj, self.scan, self.feature_name)
		for xidx in range(self.atlasobj.count):
			for yidx in range(xidx + 1, self.atlasobj.count):
				if roi_list[xidx] and roi_list[yidx]:
					continue
				newnet.data[xidx, yidx] = 0
				newnet.data[yidx, xidx] = 0
		return newnet

	def setValueAtTicks(self, xtick, ytick, value):
		self.data[self.atlasobj.ticks.index(xtick), self.atlasobj.ticks.index(ytick)] = value
		self.data[self.atlasobj.ticks.index(ytick), self.atlasobj.ticks.index(xtick)] = value

class DynamicNet(Mat):
	"""
	DynamicNet is the dynamic version of Net. It is stored as a 3-dimensional
	data array (loc x, loc y, time). One can obtain the network at a given time
	slice by using data[:, :, idx]
	"""
	def __init__(self, data, atlasobj, window_length, step_size, scan = None, feature_name = 'BOLD.net'):
		super().__init__(data, atlasobj, scan, feature_name)
		self.step_size = step_size
		self.window_length = window_length

	def append_one_slice(self, data):
		"""
		This function appends one slice of network to current dynamic networks.
		The appended slice should align with current data, or be used to create original data.
		:param data: a np (n, n) array
		:return: nothing
		"""
		data = np.reshape(data, (data.shape[0], data.shape[1], 1))
		if self.data is None:
			self.data = data
		else:
			self.data = np.concatenate((self.data, data), axis = 2)

	def loadDynamicNets(self, loadPath):
		"""
		Deprecated. Do not use this function
		"""
		raise Exception
		start = 0
		while True:
			filePath = Path(os.path.join(loadPath, 'corrcoef-%d.%d.csv' % (start, start + self.window_length)))
			if filePath.exists():
				self.dynamic_nets.append(Net(load_csvmat(filePath), self.atlasobj))
			else:
				break
			start += self.step_size

class DirectedNet(Net):
	"""
	"""
	def __init__(self, data, atlasobj, scan = None, feature_name = 'BOLD.net'):
		super().__init__(data, atlasobj, scan, feature_name)

	def iterate(self):
		for xidx in range(self.atlasobj.count):
			for yidx in range(self.atlasobj.count):
				if xidx == yidx:
					continue
				yield Connection(self.atlasobj, xidx, yidx, self.data[xidx, yidx])

	def set_data_from_connections(self, conn_list, unified_value = None):
		for conn in conn_list:
			if unified_value is not None:
				self.data[conn.xidx, conn.yidx] = unified_value
			else:
				self.data[conn.xidx, conn.yidx] = conn.value

def zero_net(atlasobj):
	return Net(np.zeros((atlasobj.count, atlasobj.count)), atlasobj)

def one_net(atlasobj):
	return Net(np.ones((atlasobj.count, atlasobj.count)), atlasobj)

def zero_attr(atlasobj):
	return Attr(np.zeros(atlasobj.count), atlasobj)

def averageNets(nets):
	"""
	This function takes in a list of Net and return an averaged Net
	"""
	data = np.zeros((nets[0].atlasobj.count, nets[0].atlasobj.count))
	for net in nets:
		data += net.data
	data /= len(nets)
	return Net(data, nets[0].atlasobj, scan = 'averaged')

def averageAttr(attr_list, result_scan = None):
	atlasobj = attr_list[0].atlasobj
	result = zero_attr(atlasobj)
	result.feature_name = attr_list[0].feature_name
	result.scan = result_scan
	for idx in range(atlasobj.count):
		result.data[idx] = np.average([attr.data[idx] for attr in attr_list])
	return result

def normalize_feature(feature_value, feature_name, atlasobj):
	if feature_name == 'BOLD.BC':
		return float(feature_value)/((atlasobj.count-1)*(atlasobj.count-2))
	elif feature_name == 'BOLD.WD':
		return float(feature_value)/(atlasobj.count - 1)
	else:
		return feature_value

def normalize_features(feature_list, feature_name, atlasobj):
	"""
	Input a list of actual values
	:param feature_list:
	:param feature_name:
	:param atlasobj:
	:return:
	"""
	normalized_feature = []
	for feat in feature_list:
		normalized_feature.append(normalize_feature(feat, feature_name, atlasobj))
	return normalized_feature

def networks_comparisons(network_list_A, network_list_B, comparison_method):
	"""
	comparison_method should be stats_utils.twoSampleTTest or stats_utils.pairedTTest
	"""
	atlasobj = network_list_A[0].atlasobj
	stat_network = zero_net(atlasobj)
	p_network = one_net(atlasobj)
	for xidx in range(atlasobj.count):
		for yidx in range(xidx+1, atlasobj.count):
			# print(atlasobj.ticks[xidx], atlasobj.ticks[yidx]) 'L32' - 'L32'
			t, tp = comparison_method([net.data[xidx, yidx] for net in network_list_A], 
									  [net.data[xidx, yidx] for net in network_list_B])
			stat_network.data[xidx, yidx] = t
			stat_network.data[yidx, xidx] = t
			p_network.data[xidx, yidx] = tp
			p_network.data[yidx, xidx] = tp
	return stat_network, p_network

def attr_comparisons(attr_list_A, attr_list_B, comparison_method, correction_method = None):
	"""
	Comparison is performed by A - B
	"""
	atlasobj = attr_list_A[0].atlasobj
	stat_attr = zero_attr(atlasobj)
	p_attr = zero_attr(atlasobj)
	for idx in range(atlasobj.count):
		t, tp = comparison_method([attr.data[idx] for attr in attr_list_A], 
								  [attr.data[idx] for attr in attr_list_B])
		stat_attr.data[idx] = t
		p_attr.data[idx] = tp
	if correction_method is not None:
		_, p_attr.data = correction_method(p_attr.data)
	return stat_attr, p_attr

def FC_values(network):
	"""
	Get FC values in a network.
	Return a list of dict, whose keys are connection ticks ('L1-L2') and FC value (as %1.4f)
	"""
	atlasobj = network.atlasobj
	ret = []
	for xidx in range(atlasobj.count):
		for yidx in range(xidx + 1, atlasobj.count):
			if network.data[xidx, yidx] != 0:
				ret.append(dict(connection = '%s-%s' % (atlasobj.ticks[xidx], atlasobj.ticks[yidx]), FC = '%1.4f' % (network.data[xidx, yidx])))
	return ret

def FC_count(FC_list):
	"""
	Input a list of strings representing FC connection ticks ('L1-L2')
	Return number of within hemisphere FC and cross hemisphere FC
	"""
	within_hemisphere_FC_count = 0
	cross_hemisphere_FC_count = 0
	for FC in FC_list:
		ticks = FC.split('-')
		if ticks[0][0] == ticks[1][0]:
			within_hemisphere_FC_count += 1
		if ticks[0][0] != ticks[1][0]:
			cross_hemisphere_FC_count += 1
	return within_hemisphere_FC_count, cross_hemisphere_FC_count
