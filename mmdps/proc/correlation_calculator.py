"""
Calculate correlation between features and clinical scores.
"""
import os
import numpy as np
from scipy import stats

from matplotlib import pyplot as plt

from mmdps.vis import line, matprocs
from mmdps.proc import loader, atlas
from mmdps.util import loadsave, mattool

class ScoreCorrelationCalculator:
	"""
	FCScoreCorrelation
	This class is used to calculate the correlation between FCs in a network
	and scores. 
	"""
	def __init__(self, mriscans, netLoader, scoreLoader, attrLoader):
		self.mriscans = mriscans
		self.netLoader = netLoader
		self.scoreLoader = scoreLoader
		self.scores_stacked = scoreLoader.loadvstack(self.mriscans)
		self.stacknets()
		self.attrLoader = attrLoader
		self.attrNames = ['BOLD.BC', 'BOLD.LE', 'BOLD.WD', 'BOLD.CCFS']
		self.attr_stacked = self.attrLoader.loadvstackmulti(self.mriscans, self.attrNames)

	def stacknets(self, f_netproc = matprocs.absolute):
		"""
		This function convert the whole 2D net into an 1D vector (horizontal)
		and stack all vector vertically.
		"""
		self.nets = self.netLoader.loadMulti(self.mriscans)
		dataList = []
		for currentNet in self.nets:
			currentNetdata = f_netproc(currentNet.data).flatten()
			dataList.append(currentNetdata)
		self.nets_stacked = np.vstack(dataList)

	def calculateCorrelationNet(self, atlasobj, scoreName):
		"""
		This function is used to calculate FC correlation with scoreName.
		The return value, rmat, pmat, contains Pearson's r and p regarding the correlation of 
		this connection with score
		"""
		matShape = (atlasobj.count, atlasobj.count)
		scoreVec = self.scores_stacked[:, self.scoreLoader.scoreNames.index(scoreName)]
		rs, ps = mattool.pearsonr(self.nets_stacked, scoreVec)
		rmat = rs.reshape(matShape)
		np.fill_diagonal(rmat, 0)
		pmat = ps.reshape(matShape)
		np.fill_diagonal(pmat, 1)
		return rmat, pmat

	def calculateCorrelationAttr(self, atlasobj, attrName, scoreName):
		"""
		This function is used to calculate correlation between one clinical scores
		and graph attributes of each brain region.
		The return value, rvec, pvec, contains Pearson's r and p regarding the correlation
		"""
		attrData = self.attr_stacked[:, atlasobj.count*self.attrNames.index(attrName):atlasobj.count*(self.attrNames.index(attrName)+1)]
		rvec = []
		pvec = []
		for colIdx in range(attrData.shape[1]):
			r, p = stats.pearsonr(attrData[:, colIdx], self.scores_stacked[:, self.scoreLoader.scoreNames.index(scoreName)])
			rvec.append(r)
			pvec.append(p)
		return rvec, pvec

	def calculateFCScoreCorrelation(self, connections, atlasobj, titlePrefix):
		"""
		Only FC in connections will be considered
		"""
		for scoreName in self.scoreLoader.scoreNames:
			rmat, pmat = self.calculateCorrelationNet(atlasobj, scoreName)
			for connection in connections:
				ticks = connection.split('-')
				xidx = atlasobj.ticks.index(ticks[0])
				yidx = atlasobj.ticks.index(ticks[1])
				if pmat[xidx, yidx] > 0.05:
					continue
				idx = xidx * atlasobj.count + yidx
				xvec = self.nets_stacked[:, idx]
				yvec = self.scores_stacked[:, self.scoreLoader.scoreNames.index(scoreName)]
				ticks = atlasobj.indexes_to_ticks([xidx, yidx])
				title = '%s-%s %s' % (ticks[0], ticks[1], scoreName)
				outfilepath = 'E:/Changgung works/20180409_tDCS_14/FC_score_correlation/%s %s-%s %s.png' % (titlePrefix, ticks[0], ticks[1], scoreName)
				plotter = line.CorrPlot(xvec, yvec, 'FC', scoreName, title, outfilepath)
				plotter.plot()

	def calculateAttributeScoreCorrelation(self, regions, atlasobj, titlePrefix, outfilepath, scoreNames = None):
		"""
		Score and graphic metrics correlation
		Specify which scores to calculate in scoreNames(list), otherwise all scores will be used
		"""
		if scoreNames is None:
			scoreNames = self.scoreLoader.scoreNames
		for scoreName in scoreNames:
			for attrName in self.attrNames:
				rvec, pvec = self.calculateCorrelationAttr(atlasobj, attrName, scoreName)
				for region in regions:
					idx = atlasobj.ticks.index(region)
					if pvec[idx] > 0.05:
						continue
					xvec = self.attr_stacked[:, atlasobj.count*self.attrNames.index(attrName)+idx]
					yvec = self.scores_stacked[:, self.scoreLoader.scoreNames.index(scoreName)]
					title = '%s %s %s' % (region, attrName, scoreName)
					currentFilePath = os.path.join(outfilepath, '%s %s %s %s.png' % (titlePrefix, region, attrName, scoreName))
					plotter = line.CorrPlot(xvec, yvec, attrName, scoreName, title, currentFilePath)
					plotter.plot()
