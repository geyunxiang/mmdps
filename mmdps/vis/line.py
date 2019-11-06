"""Line plot."""

import os
from scipy import stats
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont

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
		self.H = np.max([attr.data for attr in self.attrs])
		self.atlasobj = self.attrs[0].atlasobj
		self.count = self.atlasobj.count
		self.title = title
		self.outfilepath = outfilepath
		self.sig_positions = None
		self.plot_ticks = None
	
	def add_markers(self):
		"""
		positions - a list of index
		"""
		for plot_p, sig_flag in enumerate(self.sig_positions):
			if sig_flag != 1:
				continue
			h = np.max([attr.data[plot_p] for attr in self.attrs])
			if self.H - h > 0.2 * self.H:
				plt.plot([plot_p, plot_p], [h + 0.05 * self.H, self.H], color = 'g')
			plt.text(plot_p - 0.5, self.H, '*', fontsize = 20)

	def add_text(self, stat_list):
		"""
		sig_positions is a np.array with length = atlasobj.count
		The value at each index is 0 or 1, with 1 representing significance
		stat_list is a list of zipped value (stat, p). The length = atlasobj.count
		"""
		image = Image.open(self.outfilepath)
		width, height = image.size
		# find text height
		new_im = Image.new('RGB', (width, height), 'white')
		draw = ImageDraw.Draw(new_im)
		font = ImageFont.truetype('arial.ttf', 16)
		w, h = draw.textsize(' p = 1.234   ', font = font)
		y_maximum = 4 # how many records per column
		new_im = Image.new('RGB', (width, height + int(h * y_maximum)), 'white')
		draw = ImageDraw.Draw(new_im)
		# paste old image
		x_offset = 0
		y_offset = 0
		new_im.paste(image, (x_offset, y_offset))
		text_x_offset = 0.13 * width # experiment result magic number offset
		x_offset = text_x_offset
		y_offset = height
		y_count = 0
		x_shift = 0
		for idx, stat in enumerate(stat_list):
			if stat[1] > 0.05:
				continue
			y_count += 1
			draw.text((x_offset, y_offset), '* %s' % self.atlasobj.ticks[idx], (0, 0, 0), font = font)
			x_offset += (w-10) # magic
			x_shift += (w-10)
			draw.text((x_offset, y_offset), 't = %1.3f' % (stat[0]), (0, 0, 0), font = font)
			x_offset += w
			x_shift += w
			draw.text((x_offset, y_offset), 'p = %1.3f' % (stat[1]), (0, 0, 0), font = font)
			if y_count == y_maximum:
				y_count = 0
				y_offset = height
				x_offset += 0.05 * width
			else:
				y_offset += h
				x_offset -= x_shift
			x_shift = 0
		os.remove(self.outfilepath)
		new_im.save(self.outfilepath)

	def adjust_plot_index(self, sig_positions = None):
		"""
		adjust data and ticks according to plot_index
		return nothing, data, ticks and sig_positions are stored as local attributes
		"""
		self.plot_ticks = self.atlasobj.adjust_ticks()
		for attr in self.attrs:
			attr.data = self.atlasobj.adjust_vec(attr.data)
		if sig_positions is not None:
			self.sig_positions = self.atlasobj.adjust_vec(sig_positions)

	def adjust_RSN(self, sig_positions = None):
		"""
		adjust data and ticks according to RSN
		"""
		self.plot_ticks, _ = self.atlasobj.adjust_ticks_RSN()
		for attr in self.attrs:
			attr.data = self.atlasobj.adjust_vec_RSN(attr.data)
		if sig_positions is not None:
			self.sig_positions = self.atlasobj.adjust_vec_RSN(sig_positions)

	def adjust_circos(self, sig_positions = None):
		self.atlasobj.set_brainparts('default')
		self.plot_ticks = self.atlasobj.brainparts.get_region_list()
		for attr in self.attrs:
			attr.data = self.atlasobj.adjust_vec_Circos(attr.data)
		if sig_positions is not None:
			self.sig_positions = self.atlasobj.adjust_vec_Circos(sig_positions)		

	def plot(self, sig_positions = None, stat_list = None, adjust_method = None):
		"""
		sig_positions should be a vector of 0 and 1, where 1 stands for significance
		specify adjust_method as a string ('RSN', 'circos'). Defaults to plot_index
		"""
		plt.figure(figsize=(20, 6))
		if adjust_method == 'RSN':
			self.adjust_RSN(sig_positions)
		elif adjust_method == 'circos':
			self.adjust_circos(sig_positions)
		else:
			self.adjust_plot_index(sig_positions)
		for attr in self.attrs:
			plt.plot(range(self.count), attr.data, '.-', label = attr.name)
		plt.xlim([0, self.count-1])
		plt.ylim([0 - 0.1*self.H, self.H * 1.1])
		plt.xticks(range(self.count), self.plot_ticks, rotation=60)
		if sig_positions is not None:
			self.add_markers()
		plt.grid(True)
		plt.legend()
		plt.title(self.title, fontsize=20)
		plt.savefig(self.outfilepath, dpi=100)
		plt.close()
		if stat_list is not None:
			# add text goes AFTER the image is saved
			self.add_text(stat_list)

class DynamicLinePlot:
	"""
	This class is used to plot the time series of dynamic features.
	"""
	def __init__(self, attrs, regionIdx, stepSize, title, outfilepath):
		"""
		Attrs should be a dict of lists of attrs
		Only attrs related to region is plotted
		The key of attrs are taken as labels
		"""
		self.attrs = attrs
		self.regionIdx = regionIdx
		self.stepSize = stepSize
		self.title = title
		self.outfilepath = outfilepath

	def plot(self):
		plt.figure(figsize = (20, 6))
		for key in self.attrs:
			self.count = len(self.attrs[key])
			plt.plot(range(1, self.count+1), [attr.data[self.regionIdx] for attr in self.attrs[key]], '.-', label = key)
		plt.xlim([0, self.count+1])
		plt.xticks(range(1, self.count+1), range(1, self.count*self.stepSize, self.stepSize))
		plt.grid(True)
		plt.legend()
		plt.title(self.title, fontsize = 20)
		plt.savefig(self.outfilepath, dpi = 100)
		plt.close()

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
		plt.title(self.title + ' r:{:0.3} p:{:0.3}'.format(rvalue, pvalue))
		plt.xlabel(self.xlabel)
		plt.ylabel(self.ylabel)
		path.makedirs_file(self.outfile)
		fig.savefig(self.outfile)
		plt.close()

def plot_correlation(xvec, yvec, xlabel, ylabel, title, outfile):
	plotter = CorrPlot(xvec, yvec, xlabel, ylabel, title, outfile)
	plotter.plot()

def plot_attr_lines(attrs, title, outfilepath, sig_positions = None, stat_list = None, adjust_method = None):
	plotter = LinePlot(attrs, title, outfilepath)
	plotter.plot(sig_positions, stat_list, adjust_method)
