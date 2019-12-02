"""Feature data container.

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
from mmdps.util import dataop, path
from mmdps.util.loadsave import save_csvmat, load_csvmat

class Attr:
	"""Attr is attribute, it is a one dimensional vector.

	The dimension of the vector is atlasobj.count.
	"""
	def __init__(self, data, atlasobj, name = None):
		"""Init the attr, using data, atlasobj, and name.

		The name can be any string that can be useful.
		"""
		self.data = data
		self.atlasobj = atlasobj
		self.name = name

	def copy(self):
		"""Copy the attr."""
		newattr = Attr(self.data.copy(), self.atlasobj, self.name)
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

class DynamicAttr:
	"""
	DynamicAttr is the dynamic version of Attr.
	In static context, an Attr represents one kind of attributes of one person, containing single value for multiple
	brain regions and resulting in a 1-D vector.
	In dynamic context, a DynamicAttr represents one kind of dynamic attributes of one person, containing multiple
	values for multiple brain regions and resulting in a 2-D matrix. (num_regions X num_time_points)
	"""
	def __init__(self, atlasobj, name = None):
		self.atlasobj = atlasobj
		self.data = None
		self.name = name
		self.T = 0

	def normalize(self):
		if np.max(self.data) < 1.1:
			# already normalized
			return
		for xidx in range(self.data.shape[0]):
			for yidx in range(self.data.shape[1]):
				self.data[xidx, yidx] = normalize_feature(self.data[xidx, yidx], self.name, self.atlasobj)

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

class Net:
	"""Net is network, it is a two dimensional sqaure matrix.

	The dimension of the vector is (atlasobj.count, atlasobj.count).
	"""
	def __init__(self, data, atlasobj, name='net'):
		"""Init the net, using data, atlasobj, and name.

		The name can be any string that can be useful.
		""" 
		self.data = data # np array
		self.atlasobj = atlasobj
		self.name = name

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

	def copy(self):
		"""Copy the net."""
		newnet = Net(self.data.copy(), self.atlasobj, self.name)
		return newnet

	def copySubnetOnly(self, subAreaList):
		"""
		Return a copy of current network, but only values associated
		with the subnetwork specified by areas in the subAreaList argument
		"""
		newnet = Net(self.data.copy(), self.atlasobj, self.name)
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
		newnet = Net(self.data.copy(), self.atlasobj, self.name)
		for xidx in range(self.atlasobj.count):
			for yidx in range(self.atlasobj.count):
				if abs(self.data[xidx, yidx]) < threshold:
					newnet.data[xidx, yidx] = 0
		return newnet

	def setValueAtTicks(self, xtick, ytick, value):
		self.data[self.atlasobj.ticks.index(xtick), self.atlasobj.ticks.index(ytick)] = value
		self.data[self.atlasobj.ticks.index(ytick), self.atlasobj.ticks.index(xtick)] = value

class DynamicNet:
	"""
	Dynamic net is a collection of nets
	It needs only contain the atlasobj of the net
	"""
	def __init__(self, atlasobj, step = 3, windowLength = 100):
		self.atlasobj = atlasobj
		self.stepSize = step
		self.windowLength = windowLength
		self.dynamic_nets = []

	def loadDynamicNets(self, loadPath):
		start = 0
		while True:
			filePath = Path(os.path.join(loadPath, 'corrcoef-%d.%d.csv' % (start, start + self.windowLength)))
			if filePath.exists():
				self.dynamic_nets.append(Net(load_csvmat(filePath), self.atlasobj))
			else:
				break
			start += self.stepSize

class Mat:
	"""Mat is a general array data of any dimension, with an atlasobj and a name."""
	def __init__(self, data, atlasobj, name='mat'):
		"""Init the mat."""
		self.data = data
		self.atlasobj = atlasobj
		self.name = name

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
	return Net(data, nets[0].atlasobj, name = 'averaged')

def averageAttr(attr_list):
	atlasobj = attr_list[0].atlasobj
	result = zero_attr(atlasobj)
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

def attr_comparisons(attr_list_A, attr_list_B, comparison_method):
	atlasobj = attr_list_A[0].atlasobj
	stat_attr = zero_attr(atlasobj)
	p_attr = zero_attr(atlasobj)
	for idx in range(atlasobj.count):
		t, tp = comparison_method([attr.data[idx] for attr in attr_list_A], 
								  [attr.data[idx] for attr in attr_list_B])
		stat_attr.data[idx] = t
		p_attr.data[idx] = tp
	return stat_attr, p_attr
