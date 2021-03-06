import os
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from matplotlib import cm
from mmdps.proc import atlas, job
from mmdps.util.loadsave import load_rawtext, save_rawtext
from mmdps.util import path
from mmdps import rootconfig

CircosConfigFolder = os.path.join(rootconfig.path.data, 'braincircos', 'simpleconfig')

def color_to_str(color):
	return 'color=({},{},{})'.format(color[0], color[1], color[2])

class Chromosome:
	def __init__(self, atlasobj, chrname, configdict):
		self.atlasobj = atlasobj
		self.configdict = configdict
		self.chrname = chrname
		self.name = configdict['name']
		self.indexes = None
		self.bandtuples = None
		self.count = 0
		self.build_bands()
		self.build_bandtuples()

	def build_bands(self):
		if 'ticks' in self.configdict:
			self.indexes = self.atlasobj.ticks_to_indexes(self.configdict['ticks'])
		elif 'indexes' in self.configdict:
			self.indexes = self.configdict['indexes']
		else:
			print('Use ticks or indexes to specify brain regions.')
			raise Exception('bad chromosome')
		self.count = len(self.indexes)

	def build_bandtuples(self):
		tuples = []
		for i in range(len(self.indexes)):
			t = (self.chrname, i, i+1)
			tuples.append(t)
		self.bandtuples = tuples

class BrainParts:
	def __init__(self, configdict):
		self.configdict = configdict
		self.atlasname = self.configdict['atlas']
		self.atlasobj = atlas.get(self.atlasname)
		self.chrdict = {}
		self.build_all()

	def build_all(self):
		leftconfig = self.configdict['config'].get('left')
		if leftconfig:
			lchrs = self.build_chromosomes('L_', leftconfig)
			self.chrdict['left'] = lchrs
		rightconfig = self.configdict['config'].get('right')
		if rightconfig:
			rchrs = self.build_chromosomes('R_', rightconfig)
			self.chrdict['right'] = rchrs
		centerconfig = self.configdict['config'].get('center')
		if centerconfig:
			cchrs = self.build_chromosomes('C_', centerconfig)
			self.chrdict['center'] = cchrs
		self.chrdict['all'] = lchrs + rchrs

	def build_chromosomes(self, prefix, config):
		sections = config['sections']
		chromosomes = []
		for i, sectionconf in enumerate(sections):
			chrname = '{}{}'.format(prefix, i)
			chromo = Chromosome(self.atlasobj, chrname, sectionconf)
			chromosomes.append(chromo)
		return chromosomes

	def get_region_list(self):
		"""
		Return a list of regions in order plotted by circos
		Left and right regions are interleaved
		Also return the second element as a list of no. of nodes in each lobe
		"""
		leftconfig = self.configdict['config'].get('left')
		rightconfig = self.configdict['config'].get('right')
		region_list = []
		nodeCount = []
		for secIdx, section in enumerate(leftconfig['sections']):
			nodeCount.append(len(section['ticks'] * 2))
			for tickIdx, tick in enumerate(section['ticks']):
				# left first
				region_list.append(tick)
				region_list.append(rightconfig['sections'][secIdx]['ticks'][tickIdx])
		return (region_list, nodeCount)

class CircosConfigChromosome:
	def __init__(self, brainparts, colorlist=None):
		self.brainparts = brainparts
		self.atlasobj = self.brainparts.atlasobj
		self.chrdict = self.brainparts.chrdict
		if colorlist is None:
			colorlist = ['grey'] * self.atlasobj.count
		self.colorlist = colorlist

	def write_karyotype(self, f):
		chrfmt = 'chr - {} {} {} {} {}'  # chr - L_1 L 0 54 green
		for chromosome in self.chrdict['right']:
			chrline = chrfmt.format(chromosome.chrname, chromosome.name, 0, chromosome.count, 'green')
			f.write(chrline + '\n')
		for chromosome in reversed(self.chrdict['left']):
			chrline = chrfmt.format(chromosome.chrname, chromosome.name, 0, chromosome.count, 'green')
			f.write(chrline + '\n')

		bandfmt = 'band {} {} {} {} {} {}'  # band L_1 L1 L1 0 1 grey
		for chromosome in self.chrdict['all']:
			for i in range(chromosome.count):
				atlasindex = chromosome.indexes[i]
				bandtuple = chromosome.bandtuples[i]
				atlastick = self.atlasobj.ticks[atlasindex]
				bandline = bandfmt.format(bandtuple[0], atlastick, atlastick, bandtuple[1], bandtuple[2], self.colorlist[atlasindex])
				f.write(bandline + '\n')

	def write_labels(self, f):
		labelfmt = '{} {} {} {}'  # L_1 0 1 L1
		for chromosome in self.chrdict['all']:
			for i in range(chromosome.count):
				atlasindex = chromosome.indexes[i]
				bandtuple = chromosome.bandtuples[i]
				atlastick = self.atlasobj.ticks[atlasindex]
				labelline = labelfmt.format(bandtuple[0], bandtuple[1], bandtuple[2], atlastick)
				f.write(labelline + '\n')

	def write(self, outfolder):
		with open(os.path.join(outfolder, 'karyotype.txt'), 'w') as f:
			self.write_karyotype(f)
		with open(os.path.join(outfolder, 'atlas.labels.txt'), 'w') as f:
			self.write_labels(f)

class CircosConfigFile:
	PlotFmt = """
	<plot>
	type = heatmap
	stroke_thickness = 1p
	stroke_color = black
	file = {file}
	r1 = {r1}
	r0 = {r0}
	</plot>
	"""
	LinkFmt = """
	<link>
	file = {file}
	radius = {radius}
	bezier_radius = 0r
	thickness = {thickness}
	</link>
	"""
	def __init__(self):
		self.plotconfs = []
		self.linkconfs = []
		self.label_size = None
		self.linkThickness = 10 # default link thickness

	def add_plot(self, file):
		self.plotconfs.append(file)

	def add_link(self, file):
		self.linkconfs.append(file)

	def build_circos_conf(self, plotstrs, linkstrs):
		self.circos_template = load_rawtext(os.path.join(CircosConfigFolder, 'circos_template.conf'))
		return self.circos_template.format(plotsstr='\n'.join(plotstrs), linksstr='\n'.join(linkstrs))

	def customizeSize(self, label_size, linkThickness):
		self.label_size = label_size
		if linkThickness is not None:
			self.linkThickness = linkThickness

	def customized_rewrite(self, outfolder):
		"""
		Re-generate circos.conf to update parameters
		"""
		os.rename(os.path.join(outfolder, 'circos.conf'), os.path.join(outfolder, 'circos.conf.bk'))
		confFile = open(os.path.join(outfolder, 'circos.conf'), 'w')
		with open(os.path.join(outfolder, 'circos.conf.bk')) as bk:
			for line in bk.readlines():
				if line.find('label_size') != -1:
					line = '%s%s\n' % (line[:line.find('=')+2], self.label_size)
				confFile.write(line)
		confFile.close()
		os.remove(os.path.join(outfolder, 'circos.conf.bk'))

	def write(self, outfolder):
		plotstrs = []
		rfmt = '{:.2f}r'
		plotwidth = 0.05
		for iplot, plotconf in enumerate(self.plotconfs):
			r1f = 0.99 - iplot * plotwidth
			r0f = r1f - 0.04
			plotstr = self.PlotFmt.format(file=plotconf, r1=rfmt.format(r1f), r0=rfmt.format(r0f))
			plotstrs.append(plotstr)
		nplot = len(self.plotconfs)
		linkstrs = []
		for linkconf in self.linkconfs:
			radius = 1.0 - nplot * plotwidth
			linkstr = self.LinkFmt.format(file=linkconf, radius=rfmt.format(radius), thickness = self.linkThickness)
			linkstrs.append(linkstr)
		finalstring = self.build_circos_conf(plotstrs, linkstrs)
		fname = os.path.join(outfolder, 'circos.conf')
		save_rawtext(fname, finalstring)

class CircosLink:
	def __init__(self, net, threshold = 0, valuerange = None):
		self.net = net
		self.threshold = threshold
		if valuerange is None:
			# check for all same value
			unique = np.unique(net.data)
			if len(unique) == 1:
				self.valuerange = (0, 1)
			else:
				self.valuerange = (np.min(net.data), np.max(net.data))
		else:
			self.valuerange = valuerange
		self.brainparts = net.atlasobj.get_brainparts()
		self.chrdict = self.brainparts.chrdict
		self.data = self.net.data

	def get_mask(self):
		mask = np.zeros(self.net.data.shape, dtype=bool)
		threshold = self.threshold
		mask[np.abs(self.net.data) > threshold] = True
		mask = np.triu(mask, 1)
		return mask

	def get_line(self, chrA, idxA, chrB, idxB):
		linkfmt = '{} {} {} {} {} {} {}'  # L_1 0 1 L_1 1 2 color=(10,10,10)
		color = self.get_color(chrA, idxA, chrB, idxB)
		if color is None:
			return None
		else:
			colorstr = color_to_str(color)
			linkline = linkfmt.format(*chrA.bandtuples[idxA], *chrB.bandtuples[idxB], colorstr)
			return linkline

	def get_color(self, chrA, idxA, chrB, idxB):
		value = self.get_value(chrA, idxA, chrB, idxB)
		if value is None:
			return None
		else:
			value = self.map_value(value)
			color = self.get_cmap()(value, bytes=True)
			return color

	def get_value(self, chrA, idxA, chrB, idxB):
		row, col = self.get_rowcol(chrA, idxA, chrB, idxB)
		bmask = self.mask[row, col]
		if bmask:
			return self.data[row, col]
		else:
			return None

	def get_rowcol(self, chrA, idxA, chrB, idxB):
		row = chrA.indexes[idxA]
		col = chrB.indexes[idxB]
		return (row, col)

	def map_value(self, value):
		valuerange = self.valuerange
		a = valuerange[0]
		b = valuerange[1]
		return (value-a) / (b-a)

	def get_cmap(self):
		return cm.coolwarm

	def write(self, outfullpath):
		with open(outfullpath, 'w') as f:
			self.mask = self.get_mask()
			for chrA in self.chrdict['all']:
				for idxA in range(chrA.count):
					for chrB in self.chrdict['all']:
						for idxB in range(chrB.count):
							line = self.get_line(chrA, idxA, chrB, idxB)
							if line:
								f.write(line)
								f.write('\n')

class CircosValue:
	def __init__(self, attr, valuerange = None, cmap_str = None, colormap = None):
		"""
		Input colormap as a dict mapping values in attr.data to color etc (10, 20, 30)
		use matplotlib.colors.to_rgb('crimson') to get color tuple.
		See https://matplotlib.org/3.1.1/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py
		"""
		self.brainparts = attr.atlasobj.get_brainparts()
		if valuerange is None:
			self.valuerange = (np.min(attr.data), np.max(attr.data))
		else:
			self.valuerange = valuerange
		if cmap_str is not None:
			self.set_cmap(cmap_str)
		else:
			self.cmap = cm.Reds
		self.colormap = colormap
		self.chrdict = self.brainparts.chrdict
		self.attr = attr
		self.data = self.attr.data

	def get_line(self, chro, idx):
		valuefmt = '{} {} {} {} {}'  # L_1 0 1 0.312 color=(10,10,10)
		value = self.get_value(chro, idx)
		color = self.get_color(chro, idx)
		colorstr = color_to_str(color)
		valueline = valuefmt.format(*chro.bandtuples[idx], value, colorstr)
		return valueline

	def get_value(self, chro, idx):
		return self.data[self.get_index(chro, idx)]

	def get_index(self, chro, idx):
		return chro.indexes[idx]

	def get_color(self, chro, idx):
		value = self.get_value(chro, idx)
		if self.colormap is None:
			value = self.map_value(value)
			color = self.cmap(value, bytes=True)
			return color
		else:
			return tuple(list(channel*255 for channel in self.colormap[value]))

	def map_value(self, value):
		a = self.valuerange[0]
		b = self.valuerange[1]
		return (value-a) / (b-a)

	def set_cmap(self, cmap_str):
		if cmap_str == 'blue':
			self.cmap = cm.Blues
		elif cmap_str == 'coolwarm':
			self.cmap = cm.coolwarm
		else:
			self.cmap = cm.Reds

	def write(self, outfullpath):
		with open(outfullpath, 'w') as f:
			for chro in self.chrdict['all']:
				for idx in range(chro.count):
					line = self.get_line(chro, idx)
					f.write(line)
					f.write('\n')

class CircosPlotBuilder:
	def __init__(self, atlasobj, title, outfilepath):
		self.atlasobj = atlasobj
		self.brainparts = self.atlasobj.get_brainparts() # circosparts.json file in each atlas's folder
		self.title = title
		if outfilepath[-4:] == '.png':
			outfilepath = outfilepath[:-4]
		self.outfilepath = outfilepath
		self.outfolder, self.outfilename = os.path.split(outfilepath)
		self.circosfolder = os.path.join(self.outfolder, 'circosdata', self.outfilename)
		path.makedirs(self.circosfolder)
		self.circosConfigFile = CircosConfigFile()
		self.circoslinks = []
		self.circosvalues = []
		self.customizedSizes = False
		self.radius = None
		if atlasobj.name == 'bnatlas':
			self.customizeSize(label_size = '20p', linkThickness = '10p')
		elif atlasobj.name == 'aicha':
			self.customizeSize(label_size = '10p', linkThickness = '5p')

	def customizeSize(self, ideogram_radius = '0.8r', label_size = '40p', linkThickness = '20p'):
		"""
		input ideogram_radius as a string like '0.80r'
			- ideogram_radius controls the size of the whole ring
		input label_size as a string like '40p'
			- label_size controls the font size of the ticks (L1, R2 etc.)
		input linkThickness as an integer like 20p
			- linkThickness controls the thickness of network links(edges)
		"""
		self.customizedSizes = True
		self.radius = ideogram_radius
		self.circosConfigFile.customizeSize(label_size, linkThickness)

	def fullpath(self, *p):
		return os.path.join(self.circosfolder, *p)

	def add_circosvalue(self, circosvalue):
		"""
		Check unique value amount. If all values are the same, do not add this value 
		since circos will crash when plotting same values
		"""
		if len(np.unique(circosvalue.attr.data)) == 1:
			return
		self.circosvalues.append(circosvalue)

	def add_circoslink(self, circoslink):
		self.circoslinks.append(circoslink)

	def get_colorlist(self):
		return ['grey'] * self.atlasobj.count

	def copy_files(self):
		"""
		Copy circos basic ideogram config files.
		"""
		configfolder = os.path.join(rootconfig.path.data, 'braincircos', 'simpleconfig')
		configfiles = ['ideogram.conf', 'ticks.conf']
		for file in configfiles:
			shutil.copy2(os.path.join(configfolder, file), self.fullpath(file))
		if self.customizedSizes:
			# adjust ideogram radius
			os.rename(self.fullpath('ideogram.conf'), self.fullpath('ideogram.conf.bk'))
			ideogramFile = open(self.fullpath('ideogram.conf'), 'w')
			with open(self.fullpath('ideogram.conf.bk')) as bk:
				for line in bk.readlines():
					if line.find('radius') != -1 and line.find('=') != -1 and line.find('label_radius') == -1:
						line = '%s%sr\n' % (line[:line.find('=') + 2], self.radius)
					ideogramFile.write(line)
			ideogramFile.close()
			os.remove(self.fullpath('ideogram.conf.bk'))

	def write_files(self):
		"""
		Write net links and attributes to files.
		self.circosConfigFile would generate the circos.conf file.
		"""
		for i, circosvalue in enumerate(self.circosvalues):
			currentFile = 'attr{}.value.txt'.format(i)
			self.circosConfigFile.add_plot(currentFile)
			circosvalue.write(self.fullpath(currentFile))
		for i, circoslink in enumerate(self.circoslinks):
			currentFile = 'net{}.link.txt'.format(i)
			self.circosConfigFile.add_link(currentFile)
			circoslink.write(self.fullpath(currentFile))
		self.circosConfigFile.write(self.fullpath())
		if self.customizedSizes:
			self.circosConfigFile.customized_rewrite(self.fullpath())
		circosconfigchr = CircosConfigChromosome(self.brainparts, self.get_colorlist())
		circosconfigchr.write(self.fullpath())

	def run_circos(self):
		j = job.ExecutableJob('circos', rootconfig.path.circos, wd=self.fullpath())
		j.run()

	def plot(self, top_left = None, top_right = None, bottom_left = None, bottom_right = None):
		self.copy_files()
		self.write_files()
		self.run_circos()
		generatedpng = self.fullpath('circos.png')
		if os.path.isfile(generatedpng):
			decorator = CircosPlotDecorator(generatedpng, self.outfilepath, self.title, top_left, top_right, bottom_left, bottom_right)
			finalpng = decorator.decorate_figure()
			shutil.copy2(finalpng, self.outfilepath + '.png')

class CircosPlotDecorator():
	"""
	CircosPlotDecorator is used to add titles and detailed information on four corners of circos plot
	"""

	def __init__(self, infilepath, outfilepath, title, top_left = None, top_right = None, bottom_left = None, bottom_right = None):
		"""
		Specify detailed information (strings) to be added in a list and pass arguments to the appropriate position
		"""
		self.infilepath = infilepath
		self.outfilepath = outfilepath
		self.title = title
		if type(top_left) is str:
			top_left = [top_left]
		if type(top_right) is str:
			top_right = [top_right]
		if type(bottom_left) is str:
			bottom_left = [bottom_left]
		if type(bottom_right) is str:
			bottom_right = [bottom_right]
		self.top_left = top_left
		self.top_right = top_right
		self.bottom_left = bottom_left
		self.bottom_right = bottom_right
		self.new_image = None

	def decorate_figure(self):
		img = Image.open(self.infilepath)
		if len(self.title) > 0:
			padtop = 200
		else:
			padtop = 0
		self.new_image = Image.new('RGBA', (img.width, img.height + padtop), (255, 255, 255, 255))
		self.new_image.paste(img, (0, padtop))

		self.add_title()
		self.decorate_corner()

		newpng = self.infilepath[:-4] + '_decorated.png'
		self.new_image.save(newpng)
		return newpng

	def add_title(self):
		draw = ImageDraw.Draw(self.new_image)
		font = ImageFont.truetype('arial.ttf', 100)
		w, h = draw.textsize(self.title, font = font)
		width, height = self.new_image.size
		draw.text(((width - w) / 2, h / 2), self.title, (0, 0, 0), font = font)

	def decorate_corner(self):
		width, height = self.new_image.size
		draw = ImageDraw.Draw(self.new_image)
		font = ImageFont.truetype('arial.ttf', 72)
		if self.top_left is not None:
			h_cursor = 0
			for info in self.top_left:
				w, h = draw.textsize(info, font = font)
				draw.text((0, h_cursor + h / 2), info, (0, 0, 0), font = font)
				h_cursor += h
		if self.top_right is not None:
			h_cursor = 0
			for info in self.top_right:
				w, h = draw.textsize(info, font = font)
				draw.text((width - w, h_cursor + h / 2), info, (0, 0, 0), font = font)
				h_cursor += h
		if self.bottom_left is not None:
			w, h = draw.textsize('test text', font = font)
			h_cursor = height - len(self.bottom_left) * h - h
			for info in self.bottom_left:
				w, h = draw.textsize(info, font = font)
				draw.text((0, h_cursor + h / 2), info, (0, 0, 0), font = font)
				h_cursor += h
		if self.bottom_right is not None:
			w, h = draw.textsize('test text', font = font)
			h_cursor = height - len(self.bottom_right) * h - h
			for info in self.bottom_right:
				w, h = draw.textsize(info, font = font)
				draw.text((width - w, h_cursor + h / 2), info, (0, 0, 0), font = font)
				h_cursor += h

if __name__ == '__main__':
	netname = 'bold_net'
	title = 'TestCircos'
	outfilepath = 'boldnet'

	fu = None # Fusion object
	mriscan = 'zhang_20101010'

	atlasobj = fu.atlasobj
	net = fu.nets.load(mriscan, netname)
	attr = fu.attrs.load(mriscan, 'bold_interWD')
	builder = CircosPlotBuilder(atlasobj, title, outfilepath)
	builder.add_circosvalue(CircosValue(attr))
	builder.add_circosvalue(CircosValue(attr, (0, 50)))
	builder.add_circosvalue(CircosValue(attr, (0, 100)))
	builder.add_circoslink(CircosLink(net))
	# builder.customizeSize('0.83r', '40p') # brodmann_lr and brodmann_lrce
	builder.plot()
