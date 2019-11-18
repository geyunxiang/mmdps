"""Brain atlas tools.

Access brain atlases.
"""

import os
import numpy as np
# from .. import rootconfig
# from ..util import loadsave
# from ..vis import bnv
# from ..util import dataop
from mmdps import rootconfig
from mmdps.util import loadsave, dataop
from mmdps.vis import bnv
import nibabel as nib

atlas_list = ['brodmann_lr', 'brodmann_lrce', 'aal', 'aicha', 'bnatlas']

class Atlas:
	"""The brain atlas.

	Init use a description desc, check atlas folder for example.
	Can be used without actual atlas nii. If do have nii, it is in atlasfolder.
	"""
	def __init__(self, descdict, atlasfolder=None):
		"""Init the atlas object."""
		# the original description dict
		self.dd = descdict
		# the name of the atlas
		self.name = self.dd['name']
		# if atlasfolder not specified, use default
		if atlasfolder is None:
			self.atlasfolder = os.path.join(rootconfig.path.atlas, self.name)
		else:
			self.atlasfolder = atlasfolder
		# brief description
		self.brief = self.dd['brief']
		# total region count
		self.count = self.dd['count']
		# the regions list, they are the numbers appearred in nii file, sequentially, except 0.
		self.regions = self.dd['regions']
		# the ticks list, correspond to regions
		self.ticks = self.dd['ticks']
		# sub_networks
		self.sensorimotor_ticks = self.dd.get('sensory motor ticks', None)
		# the plotindexes list, n means it is the nth to be ploted.
		self.plotindexes = self.dd['plotindexes']
		# nodefile for use with brainnet viewer.
		if 'nodefile' in self.dd:
			self.nodefile = self.fullpath(self.dd['nodefile'])
			self.bnvnode = bnv.BNVNode(self.nodefile)
		# ticks_adjusted is the ticks list, adjusted using plotindexes.
		self.ticks_adjusted = self.adjust_ticks()
		# leftrightindexes in the indexes split into left and right.
		self.leftrightindexes = self.dd.get('leftrightindexes', None)
		if self.leftrightindexes:
			# indexes_fliplr is indexes with corresponding Ln and Rn flipped.
			self.indexes_fliplr = self.build_indexes_fliplr()
		# volumes to access the actual nii file.
		if 'volumes' in self.dd:
			self.add_volumes(self.dd['volumes'])
		# circos parts config folder
		self.circosfolder = self.fullpath()
		self.brainparts = None

	def fullpath(self, *p):
		"""fullpath for atlas folder."""
		return os.path.join(self.atlasfolder, *p)

	def set_brainparts(self, name):
		from ..vis import braincircos
		circosfile = 'circosparts_{}.json'.format(name)
		self.brainparts = braincircos.BrainParts(loadsave.load_json(os.path.join(self.circosfolder, circosfile)))
	
	def get_brainparts(self):
		if self.brainparts:
			return self.brainparts
		self.set_brainparts('default')
		return self.brainparts

	def add_volumes(self, volumes):
		"""Add volumes for actual nii files."""
		self.volumes = {}
		for volumename in volumes:
			volumes[volumename]['niifile'] = self.fullpath(volumes[volumename]['niifile'])
			self.volumes[volumename] = volumes[volumename]

	def get_volume(self, volumename):
		"""Get one volume using volumename."""
		return self.volumes[volumename]

	def ticks_to_regions(self, ticks):
		"""Convert ticks to regions."""
		if not hasattr(self, '_tickregiondict'):
			self._tickregiondict = dict([(k, v) for k, v in zip(self.ticks, self.regions)])
		regions = [self._tickregiondict[tick] for tick in ticks]
		return regions

	def regions_to_indexes(self, regions):
		"""Convert regions to indexes."""
		if not hasattr(self, '_regionindexdict'):
			self._regionindexdict = dict([(k, i) for i, k in enumerate(self.regions)])
		indexes = [self._regionindexdict[region] for region in regions]
		return indexes

	def ticks_to_indexes(self, ticks):
		"""
		Convert ticks to indexes.
		ticks should be a list of tick, like ['L1', 'R2'] etc
		"""
		if not hasattr(self, '_tickindexdict'):
			self._tickindexdict = dict([(k, i) for i, k in enumerate(self.ticks)])
		indexes = [self._tickindexdict[tick] for tick in ticks]
		return indexes

	def indexes_to_ticks(self, indexes):
		"""
		Convert indexes to ticks.
		indexes should be a list of index, like [1, 2, 3] etc
		"""
		return [self.ticks[index] for index in indexes]

	def build_indexes_fliplr(self):
		lrindex = self.leftrightindexes
		n = self.count
		lindex = lrindex[:n//2]
		rindex = lrindex[n//2:]
		indexes = list(range(n))
		for li, ri in zip(lindex, rindex):
			indexes[li] = ri
			indexes[ri] = li
		return indexes

	def create_sub(self, subatlasname, subindexes):
		"""Create a sub atlas using specified sub indexes.
		
		Create a sub atlas with name and sub indexes. The new sub atlas can be used
		just like a normal atlas.
		"""
		subdd = {}
		subdd['name'] = subatlasname
		subdd['brief'] = '{}, subnet based on {}'.format(subatlasname, self.name)
		subdd['count'] = len(subindexes)
		subdd['regions'] = dataop.sub_list(self.regions, subindexes)
		subdd['ticks'] = dataop.sub_list(self.ticks, subindexes)
		rawsubplotindexes = dataop.sub_list(self.plotindexes, subindexes)
		subdd['plotindexes'] = np.argsort(rawsubplotindexes)
		subatlasobj = Atlas(subdd)
		subatlasobj.bnvnode = self.bnvnode.copy_sub(subindexes)
		return subatlasobj

	def adjust_ticks(self):
		"""Adjust ticks according to plotindexes."""
		adjticks = [None] * self.count
		for i in range(self.count):
			realpos = self.plotindexes[i]
			adjticks[i] = self.ticks[realpos]
		return adjticks

	def adjust_vec(self, vec):
		"""Adjust a vector according to plotindexes."""
		vec_adjusted = np.zeros(vec.shape)
		for i in range(self.count):
			realpos = self.plotindexes[i]
			vec_adjusted[i] = vec[realpos]
		return vec_adjusted

	def adjust_mat(self, sqmat):
		"""
		Adjust a matrix according to plotindexes.
		Both columns and rows are adjusted.
		"""
		mat1 = np.empty(sqmat.shape)
		mat2 = np.empty(sqmat.shape)
		for i in range(self.count):
			realpos = self.plotindexes[i]
			mat1[i, :] = sqmat[realpos, :]
		for i in range(self.count):
			realpos = self.plotindexes[i]
			mat2[:, i] = mat1[:, realpos]
		return mat2

	def adjust_mat_col(self, mat):
		"""Adjust matrix columns according to plotindexes.

		Only columns are adjusted, rows not adjusted.
		"""
		mat1 = np.empty(mat.shape)
		for i in range(self.count):
			realpos = self.plotindexes[i]
			mat1[:, i] = mat[:, realpos]
		return mat1

	def adjust_mat_row(self, mat):
		"""Adjust matrix rows according to plotindexes.
		
		Only rows are adjusted, columns not adjusted.
		"""
		mat1 = np.empty(mat.shape)
		for i in range(self.count):
			realpos = self.plotindexes[i]
			mat1[i, :] = mat[realpos, :]
		return mat1

	def check_RSN(self):
		if not hasattr(self, 'RSNConfig'):
			self.RSNConfig = loadsave.load_json(self.fullpath('RSN_%s.json' % self.name))

	def adjust_mat_RSN(self, sqmat):
		"""
		Adjust a matrix according to RSN config file.
		Return the adjusted matrix
		"""
		self.check_RSN()
		mat1 = np.empty(sqmat.shape)
		mat2 = np.empty(sqmat.shape)
		adjustedTicks = []
		for RSN, nodeList in self.RSNConfig['ticks dict'].items():
			adjustedTicks += nodeList
		for i in range(self.count):
			realpos = self.ticks.index(adjustedTicks[i])
			mat1[i, :] = sqmat[realpos, :]
		for i in range(self.count):
			realpos = self.ticks.index(adjustedTicks[i])
			mat2[:, i] = mat1[:, realpos]
		return mat2

	def adjust_ticks_RSN(self):
		"""
		Return a tuple.
		The first element is the adjusted list of ticks according to RSN config file.
		The second element is a list of no. of nodes in each RSN (used for minor ticks vline and hline)
		"""
		self.check_RSN()
		nodeCount = []
		adjustedTicks = []
		for RSN, nodeList in self.RSNConfig['ticks dict'].items():
			nodeCount.append(len(nodeList))
			adjustedTicks += nodeList
		return (adjustedTicks, nodeCount)

	def adjust_vec_RSN(self, vec):
		"""
		Return the adjusted vector.
		Adjust order of data in vec according to RSN
		"""
		self.check_RSN()
		vec_adjusted = np.zeros(vec.shape)
		adjustedTicks, _ = self.adjust_ticks_RSN()
		for i in range(self.count):
			realpos = self.ticks.index(adjustedTicks[i])
			vec_adjusted[i] = vec[realpos]
		return vec_adjusted

	def get_RSN_list(self):
		"""
		Return a list of RSN strs
		"""
		self.check_RSN()
		return self.RSNConfig['RSN order']

	def adjust_vec_Circos(self, vec):
		vec_adjusted = np.zeros(vec.shape)
		self.set_brainparts('default')
		adjustedTicks, nodeCount = self.brainparts.get_region_list()
		for i in range(self.count):
			realpos = self.ticks.index(adjustedTicks[i])
			vec_adjusted[i] = vec[realpos]
		return vec_adjusted

def get(atlasname):
	"""Get an atlasobj with name.
	
	This is typically what you want when to get a atlas object.
	"""
	jsonFileName = atlasname + '.json'
	jsonFilePath = os.path.join(rootconfig.path.atlas, jsonFileName)
	atlasconf = loadsave.load_json(jsonFilePath)
	return Atlas(atlasconf)

def getbywd():
	"""Get an atlasobj by working directory.

	If current working directory is xx/xx/aal, then it will return an aal atlasobj.
	Use this when writing processing scripts. It will work regardless of the actual
	atlas.
	"""
	atlasname = os.path.basename(os.getcwd())
	return get(atlasname)

def getbyenv(atlasname_default='aal'):
	"""Get an atlasobj by environment variable MMDPS_CUR_ATLAS.

	If there is a environment variable MMDPS_CUR_ATLAS. Return the atlasobj specified
	by atlas name. Otherwise return the atlasobj of atlasname_default.
	Use this when writing processing scripts that should run in every atlases. 
	"""
	atlasname = os.environ.get('MMDPS_CUR_ATLAS')
	if atlasname == None:
		print('MMDPS_CUR_ATLAS not set, use default', atlasname_default)
		atlasname = atlasname_default
	return get(atlasname)

def color_atlas_region(atlasobj, regions, colors, outfilepath, resolution = '1mm'):
	"""
	This function is used to color one or several regions in an atlas.
	An nii file is saved where the specified region is set to 1 and other areas to 0
	Input 
		- regions: a string or a list of strings
		- colors: int or a list of int
	Note: if both regions and colors are lists, these two must have the same length
	"""
	if type(regions) is list and type(colors) is list and len(regions) != len(colors):
		print('You must specify colors for each regions to label, or specify a single color')
		raise Exception('Number of colors and regions not match')
	atlasImg = loadsave.load_nii(atlasobj.get_volume(resolution)['niifile'])
	atlasData = atlasImg.get_data()
	newAtlasData = atlasData.copy()
	if type(regions) is list and type(colors) is list:
		# each color for each region
		newAtlasData = np.zeros(newAtlasData.shape)
		for region, color in zip(regions, colors):
			regionMask = atlasData.copy()
			regionMask[regionMask != atlasobj.regions[atlasobj.ticks.index(region)]] = 0
			regionMask[regionMask == atlasobj.regions[atlasobj.ticks.index(region)]] = color
			newAtlasData += regionMask
	elif type(regions) is list and type(colors) is int:
		# one color for each region
		newAtlasData = np.zeros(newAtlasData.shape)
		for region in regions:
			regionMask = atlasData.copy()
			regionMask[regionMask != atlasobj.regions[atlasobj.ticks.index(region)]] = 0
			regionMask[regionMask == atlasobj.regions[atlasobj.ticks.index(region)]] = colors
			newAtlasData += regionMask
	elif type(regions) is str and type(colors) is int:
		# one color for one region
		newAtlasData[newAtlasData != atlasobj.regions[atlasobj.ticks.index(regions)]] = 0
		newAtlasData[newAtlasData == atlasobj.regions[atlasobj.ticks.index(regions)]] = colors
	else:
		raise Exception('Unsupported combinations. regions as %s, colors as %s.' % (type(regions), type(colors)))
	newAtlasImg = nib.Nifti1Image(newAtlasData, atlasImg.affine, atlasImg.header)
	nib.save(newAtlasImg, outfilepath)

def region_overlap_report(regionName, atlasBase, atlasTarget):
	"""
	This function is used to generate a region overlap report. It is used to find which regions a given
	area in an atlas (base) correspond to in another atlas (target). 
	The returned list is sorted according to overlap ratio. Each element is a tuple with the region name, counts and ratio
	"""
	regionData = atlasBase.regions[atlasBase.ticks.index(regionName)]
	atlasBaseImg = loadsave.load_nii(atlasBase.get_volume('1mm')['niifile'])
	atlasTargetImg = loadsave.load_nii(atlasTarget.get_volume('1mm')['niifile'])
	atlasBaseData = atlasBaseImg.get_data()
	atlasTargetData = atlasTargetImg.get_data()
	maskMatrix = atlasTargetData.copy()
	maskMatrix[atlasBaseData == regionData] = 1
	maskMatrix[atlasBaseData != regionData] = 0
	maskedTargetMatrix = np.multiply(atlasTargetData, maskMatrix)
	unique, counts = np.unique(maskedTargetMatrix, return_counts = True)
	resultList = []
	for areaData, count in zip(unique, counts):
		if areaData == 0:
			continue
		descriptionTuple = (atlasTarget.ticks[atlasTarget.regions.index(areaData)], '%d/%s' % (count, atlasTarget.get_volume('1mm')['regioncounts'][atlasTarget.regions.index(areaData)]), float(count)/int(atlasTarget.get_volume('1mm')['regioncounts'][atlasTarget.regions.index(areaData)]))
		resultList.append(descriptionTuple)
	resultList = sorted(resultList, key = lambda x: int(x[1].split('/')[0]), reverse = True)
	return resultList
