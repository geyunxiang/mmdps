"""
Plot network heatmap.

"""
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm
from mmdps.util import path

class HeatmapPlot:
	"""The heatmap plot."""
	def __init__(self, net, title, outfilepath, valuerange=(-1.0, 1.0)):
		"""Init the heatmap.
		net, the network.
		title, the image titile.
		outfilepath, the output image path.
		valuerange, the valuerange of the net.
		"""
		self.net = net
		self.atlasobj = self.net.atlasobj
		self.count = self.atlasobj.count
		self.title = title
		self.outfilepath = outfilepath
		self.valuerange = valuerange
		self.cmap = self.get_cmap()

	def get_cmap(self):
		"""Get default cmap use valuerange.
		
		If all positive, use Greys.
		If have negative, use coolwarm.
		"""
		if self.valuerange[0] >= 0:
			return matplotlib.cm.Greys
		else:
			return matplotlib.cm.coolwarm

	def set_cmap(self, cmap):
		"""
		cmap should be one of matplotlib.cm.xxx
		see https://matplotlib.org/gallery/color/colormap_reference.html for a list of cmaps
		"""
		self.cmap = cmap

	def plot(self):
		"""Do the plot."""
		fig = plt.figure(figsize=(20, 20))
		netdata_adjusted = self.atlasobj.adjust_mat(self.net.data)
		netdata_adjusted = np.nan_to_num(netdata_adjusted)
		axim = plt.imshow(netdata_adjusted, interpolation='none', cmap=self.cmap,
						  vmin=self.valuerange[0], vmax=self.valuerange[1])
		nrow, ncol = netdata_adjusted.shape
		ax = fig.gca()
		ax.set_xticks(range(self.count))
		ax.set_xticklabels(self.atlasobj.ticks_adjusted, rotation=90)
		ax.set_yticks(range(self.count))
		ax.set_yticklabels(self.atlasobj.ticks_adjusted)
		ax.set_xlim(-0.5, ncol-0.5)
		ax.set_ylim(nrow-0.5, -0.5)
		fig.colorbar(axim, fraction=0.046, pad=0.04)
		plt.title(self.title, fontsize=24)
		path.makedirs_file(self.outfilepath)
		plt.savefig(self.outfilepath, dpi=100)
		plt.close()

class HeatmapPlotRows:
	"""The heatmap rows plot."""
	def __init__(self, atlasobj, rowsmat, rowsticks, title, outfilepath, valuerange=(-1.0, 1.0)):
		"""Init the heatmap rows.
		atlasobj, the atlas object.
		rowsmat, the rows matrix, each row acts as an attribute.
		rowsticks, the rows ticks, each row's y tick label.
		title, the image titile.
		outfilepath, the output image path.
		valuerange, the valuerange of the net.
		"""
		self.rowsmat = rowsmat
		self.rowsticks = rowsticks
		self.atlasobj = atlasobj
		self.count = self.atlasobj.count
		self.title = title
		self.outfilepath = outfilepath
		self.valuerange = valuerange

	def get_cmap(self):
		"""Get the color map."""
		if self.valuerange[0] >= 0:
			return matplotlib.cm.Greys
		else:
			return matplotlib.cm.coolwarm

	def plot(self):
		"""Do the plot."""
		fig = plt.figure(figsize=(20, 8))
		netdata_adjusted = self.atlasobj.adjust_mat_col(self.rowsmat)
		netdata_adjusted = np.nan_to_num(netdata_adjusted)
		axim = plt.imshow(netdata_adjusted, interpolation='none', cmap=self.get_cmap(),
						  vmin=self.valuerange[0], vmax=self.valuerange[1])
		nrow = self.rowsmat.shape[0]
		_, ncol = netdata_adjusted.shape
		ax = fig.gca()
		ax.set_xticks(range(self.count))
		ax.set_xticklabels(self.atlasobj.ticks_adjusted, rotation=90)
		ax.set_yticks(range(nrow))
		ax.set_yticklabels(self.rowsticks)
		ax.set_xlim(-0.5, ncol-0.5)
		ax.set_ylim(nrow-0.5, -0.5)
		#fig.colorbar(axim)
		plt.title(self.title, fontsize=24)
		path.makedirs_file(self.outfilepath)
		plt.savefig(self.outfilepath, dpi=100)
		plt.close()
