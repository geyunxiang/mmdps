"""Line plot."""

from scipy import stats
from matplotlib import pyplot as plt

# from ..proc import atlas
# from ..util import path
from mmdps.util import path

class LinePlot:
	"""Line plot to plot attrs."""
	def __init__(self, attrs, title, outfilepath):
		"""Init the plot.

		attrs, a list of attrs to plot in the same figure. The attr.name is used for legend.
		title, the image title.
		outfilepath, the output file path.
		"""
		self.attrs = attrs
		self.atlasobj = self.attrs[0].atlasobj
		self.count = self.atlasobj.count
		self.title = title
		self.outfilepath = outfilepath
		
	def plot(self):
		"""Do the plot."""
		fig = plt.figure(figsize=(20, 6))
		# plt.hold(True)
		for attr in self.attrs:
			attrdata_adjusted = self.atlasobj.adjust_vec(attr.data)
			plt.plot(range(self.count), attrdata_adjusted, '.-', label=attr.name)
		plt.xlim([0, self.count-1])
		plt.xticks(range(self.count), self.atlasobj.ticks_adjusted, rotation=60)
		plt.grid(True)
		plt.legend()
		plt.title(self.title, fontsize=20)
		plt.savefig(self.outfilepath, dpi=100)
		plt.close()

class OverlappedLinePlot:
	"""
	Multiple line plot to show changes of attributes belonging to one brain region.
	"""
	def __init__(self, attrs, title, outfilepath):
		"""
		attrs - A list of lists. Each list contains
		"""

class CorrPlot:
	"""
	This class is used to generate correlation, usually correlation between FC/graph
	attributes and clinical scores
	"""
	def __init__(self, xvec, yvec, xlabel, ylabel, title, outfile):
		self.xvec = xvec
		self.yvec = yvec
		self.title = title
		self.outfile = outfile
		self.xlabel = xlabel
		self.ylabel = ylabel

	def plot(self):
		slope, intercept, rvalue, pvalue, stderr = stats.linregress(self.xvec, self.yvec)
		fig = plt.figure(figsize=(8, 6))
		plt.plot(self.xvec, self.yvec, 'o')
		plt.hold(True)
		a = slope
		b = intercept
		xlim = plt.gca().get_xlim()
		x0 = xlim[0]
		x1 = xlim[1]
		plt.plot(xlim, [a*x0+b, a*x1+b])
		plt.title(self.title + ' r:{:0.5} p:{:0.5}'.format(rvalue, pvalue))
		plt.xlabel(self.xlabel)
		plt.ylabel(self.ylabel)
		path.makedirs_file(self.outfile)
		fig.savefig(self.outfile)
		plt.close()
