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
	"""
	A Chromosome is a lobe in the brain, such as Frontal, Parietal etc.
	It contains a list of brain regions.
	The actual index in data is stored at self.indexes.
	"""
	def __init__(self, atlasobj, chrname, configdict):
		self.atlasobj = atlasobj
		self.configdict = configdict
		self.chrname = chrname
		self.name = configdict['name']
		self.indexes = None
		self.bandtuples = None
		self.count = 0
		self.region_names = False
		self.build_bands()
		self.build_bandtuples()

	def build_bands(self):
		if 'ticks' in self.configdict:
			self.indexes = self.atlasobj.ticks_to_indexes(self.configdict['ticks'])
		elif 'indexes' in self.configdict:
			self.indexes = self.configdict['indexes']
		elif 'region_names' in self.configdict:
			self.region_names = True
			self.indexes = [self.atlasobj.region_names.index(name) for name in self.configdict['region_names']]
		else:
			print('Use ticks, indexes or region_names to specify brain regions.')
			raise Exception('bad chromosome')
		self.count = len(self.indexes)

	def build_bandtuples(self):
		tuples = []
		for i in range(len(self.indexes)):
			t = (self.chrname, i, i+1)
			tuples.append(t)
		self.bandtuples = tuples

	def get_region_name(self, idx):
		if self.region_names:
			return self.atlasobj.region_names[idx]
		else:
			return self.atlasobj.ticks[idx]

class BrainParts:
	"""
	A structure defining Lobes, regions and ticks, corresponding to ideogram/karyotype in circos.
	I.e., the outer main ring.
	Constructed by loading json config file in atlas/<atlas_name>/circosparts_default.json etc.
	"""
	def __init__(self, configdict):
		self.configdict = configdict
		self.atlasname = self.configdict['atlas']
		self.atlasobj = atlas.get(self.atlasname)
		self.chrdict = {}
		self.build_all()

	def build_all(self):
		leftconfig = self.configdict['config'].get('left')
		lchrs = []
		rchrs = []
		cchrs = []
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
		self.chrdict['all'] = lchrs + rchrs + cchrs

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
				atlastick = chromosome.get_region_name(atlasindex)
				bandline = bandfmt.format(bandtuple[0], atlastick, atlastick, bandtuple[1], bandtuple[2], self.colorlist[atlasindex])
				f.write(bandline + '\n')

	def write_labels(self, f):
		labelfmt = '{} {} {} {}'  # L_1 0 1 L1
		for chromosome in self.chrdict['all']:
			for i in range(chromosome.count):
				atlasindex = chromosome.indexes[i]
				bandtuple = chromosome.bandtuples[i]
				atlastick = chromosome.get_region_name(atlasindex)
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
	DirectedPlotFmt = """
	<plot>
	type = scatter
	file = {file}
	glyph = triangle
	glyph_size = 48p
	min = 0
	max = 1
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
		self.direction_confs = []
		self.linkconfs = []
		self.label_size = None
		self.linkThickness = 20 # default link thickness

	def add_plot(self, file):
		self.plotconfs.append(file)

	def add_link(self, file):
		self.linkconfs.append(file)

	def add_direction(self, file):
		self.direction_confs.append(file)

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
		# heatmap
		minr = 1
		iplot = 0
		for plotconf in self.plotconfs:
			r1f = 0.99 - iplot * plotwidth
			r0f = r1f - 0.04
			minr = r0f
			plotstr = self.PlotFmt.format(file=plotconf, r1=rfmt.format(r1f), r0=rfmt.format(r0f))
			plotstrs.append(plotstr)
			iplot += 1
		for direction_conf in self.direction_confs:
			r1f = minr - 0.02
			r0f = r1f
			minr = r0f
			plotstr = self.DirectedPlotFmt.format(file=direction_conf, r1 = rfmt.format(r1f), r0 = rfmt.format(r0f))
			plotstrs.append(plotstr)
			iplot += 1
		linkstrs = []
		for linkconf in self.linkconfs:
			radius = minr
			if radius == 1:
				# if plot undirected links
				radius = 0.99
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

		self.data = self.net.data

	def set_brainparts(self, brainparts):
		self.brainparts = brainparts
		self.chrdict = self.brainparts.chrdict

	def get_mask(self):
		mask = np.zeros(self.net.data.shape, dtype=bool)
		threshold = self.threshold
		mask[np.abs(self.net.data) > threshold] = True
		# mask = np.triu(mask, 1)
		return mask

	def get_line(self, chrA, idxA, chrB, idxB):
		linkfmt = '{} {} {} {} {} {} {}'  # L_1 0 1 L_1 1 2 color=(10,10,10)
		color = self.get_color(chrA, idxA, chrB, idxB)
		if color is None:
			return None
		else:
			colorstr = color_to_str(color)
			# python3 starred expression: expand iterables to positional arguments
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

class CircosDirectedLink(CircosLink):
	def get_mask(self):
		mask = np.zeros(self.net.data.shape, dtype=bool)
		threshold = self.threshold
		mask[np.abs(self.net.data) > threshold] = True
		return mask

	def write(self, linkpath, endpath):
		link_file = open(linkpath, 'w')
		end_file = open(endpath, 'w')
		end_node_list = []
		self.mask = self.get_mask()
		for chrA in self.chrdict['all']:
			for idxA in range(chrA.count):
				for chrB in self.chrdict['all']:
					for idxB in range(chrB.count):
						line = self.get_line(chrA, idxA, chrB, idxB)
						if line:
							link_file.write(line)
							link_file.write('\n')
							end_node = ' '.join(line.split(' ')[3:6])
							if end_node in end_node_list:
								continue
							# link to
							end_node_list.append(end_node)
							end_file.write(' '.join(line.split(' ')[3:6]) + ' 0 ' + line.split(' ')[-1] + '\n')
		link_file.close()
		end_file.close()

class CircosValue:
	def __init__(self, attr, valuerange = None, cmap_str = None, colormap = None):
		"""
		Input colormap as a dict mapping values in attr.data to color etc (10, 20, 30)
		use matplotlib.colors.to_rgb('crimson') to get color tuple.
		See https://matplotlib.org/3.1.1/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py
		"""
		if valuerange is None:
			self.valuerange = (np.min(attr.data), np.max(attr.data))
		else:
			self.valuerange = valuerange
		if cmap_str is not None:
			self.set_cmap(cmap_str)
		else:
			self.cmap = cm.Reds
		self.colormap = colormap
		self.attr = attr
		self.data = self.attr.data

	def set_brainparts(self, brainparts):
		self.brainparts = brainparts
		self.chrdict = self.brainparts.chrdict

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
	def __init__(self, atlasobj, title, outfilepath, plot_config = None):
		if plot_config is None:
			plot_config = {}
		self.atlasobj = atlasobj
		if plot_config.get('draw_RSN', False):
			self.brainparts = BrainParts(self.atlasobj.get_brainparts_config('RSN')) # circosparts.json file in each atlas's folder
		else:
			self.brainparts = BrainParts(self.atlasobj.get_brainparts_config()) # circosparts.json file in each atlas's folder
		self.title = title
		if outfilepath[-4:] == '.png':
			outfilepath = outfilepath[:-4]
		self.outfilepath = outfilepath
		self.outfolder, self.outfilename = os.path.split(outfilepath)
		self.circosfolder = os.path.join(self.outfolder, 'circosdata', self.outfilename)
		path.makedirs(self.circosfolder)
		self.circosConfigFile = CircosConfigFile()
		self.circoslinks = []
		self.circos_directed_links = []
		self.circosvalues = []
		self.ideogram_radius = None
		self.colorlist = None
		if atlasobj.name == 'bnatlas':
			plot_config['region_tick_size'] = '20p'
			plot_config['link_thickness'] = '10p'
		elif atlasobj.name == 'aicha':
			plot_config['region_tick_size'] = '10p'
			plot_config['link_thickness'] = '5p'
		self.customizeSize(plot_config)

	def customizeSize(self, plot_config):
		"""
		Configable fields in plot_config:
		* General
			- 'draw_RSN': True or False (Default). Whether draw RSN according to circosparts_RSN.json
		* Ideogram (main ring, outer ring, with brain regions on it)
			- 'ideogram_radius': Specify as '0.8r', '0.6r' etc
			- 'ideogram_show_label': 'yes' or 'no'. Whether show 'Frontal' etc text
			- 'ideogram_thickness': '20p', '40p' etc. Controls the thickness of ideogram.
		* Ticks (small separating lines on the ideogram)
			- 'tick_radius': Specify as '1r-20p', '1r-30p' etc. Normally '1r-<ideogram_thickness>'
			- 'tick_thickness': '2p', '10p' etc
			- 'tick_color': 'black', 'red' etc
			- 'tick_size': '10p', '20p' etc. Normally equals 'ideogram_thickness'
		* Region name
			- 'region_tick_size': Specify as '40p' etc. Controls the text size of brain regions ('L1', 'R2' etc.)
		* Link (connections)
			- 'link_thickness': Specify as '10p', '5p' etc. Controls the line thickness of link.
		"""
		self.ideogram_radius = plot_config.get('ideogram_radius', '0.8r')
		self.ideogram_show_label = plot_config.get('ideogram_show_label', 'yes')
		self.ideogram_thickness = plot_config.get('ideogram_thickness', '20p')
		self.tick_radius = plot_config.get('tick_radius', '1r')
		self.tick_thickness = plot_config.get('tick_thickness', '2p')
		self.tick_color = plot_config.get('tick_color', 'black')
		self.tick_size = plot_config.get('tick_size', '10p')
		self.circosConfigFile.customizeSize(plot_config.get('region_tick_size', '40p'), plot_config.get('link_thickness', '20p'))

	def fullpath(self, *p):
		return os.path.join(self.circosfolder, *p)

	def add_circosvalue(self, circosvalue):
		"""
		Check unique value amount. If all values are the same, do not add this value 
		since circos will crash when plotting same values
		"""
		circosvalue.set_brainparts(self.brainparts)
		if len(np.unique(circosvalue.attr.data)) == 1:
			return
		self.circosvalues.append(circosvalue)

	def add_circoslink(self, circoslink):
		circoslink.set_brainparts(self.brainparts)
		self.circoslinks.append(circoslink)

	def add_circos_directed_link(self, circos_directed_link):
		circos_directed_link.set_brainparts(self.brainparts)
		self.circos_directed_links.append(circos_directed_link)

	def set_colorlist(self, colorlist):
		"""
		Set the color of each region on the ideogram
		:param colorlist: A list of str of color corresponding to each region in atlasobj
		:return:
		"""
		self.colorlist = colorlist

	def get_colorlist(self):
		"""
		Config color of bands (each brain region) on the ideogram (main ring)
		:return:
		"""
		if self.colorlist is None:
			return ['grey'] * self.atlasobj.count
		else:
			return self.colorlist

	def copy_files(self):
		"""
		Copy circos basic ideogram config files.
		"""
		configfolder = os.path.join(rootconfig.path.data, 'braincircos', 'simpleconfig')
		configfiles = ['ideogram.conf', 'ticks.conf']
		for file in configfiles:
			shutil.copy2(os.path.join(configfolder, file), self.fullpath(file))

		os.rename(self.fullpath('ideogram.conf'), self.fullpath('ideogram.conf.bk'))
		ideogramFile = open(self.fullpath('ideogram.conf'), 'w')
		with open(self.fullpath('ideogram.conf.bk')) as bk:
			for line in bk.readlines():
				if line.find('radius') != -1 and line.find('=') != -1 and line.find('label_radius') == -1:
					line = '%s%s\n' % (line[:line.find('=') + 2], self.ideogram_radius)
				if line.find('show_label') != -1 and line.find('=') != -1:
					line = '%s%s\n' % (line[:line.find('=') + 2], self.ideogram_show_label)
				if line.find('thickness') != -1 and line.find('=') != -1 and line.find('stroke_thickness') == -1:
					line = '%s%s\n' % (line[:line.find('=') + 2], self.ideogram_thickness)
				ideogramFile.write(line)
		ideogramFile.close()
		os.remove(self.fullpath('ideogram.conf.bk'))

		os.rename(self.fullpath('ticks.conf'), self.fullpath('ticks.conf.bk'))
		ticksFile = open(self.fullpath('ticks.conf'), 'w')
		with open(self.fullpath('ticks.conf.bk')) as bk:
			for line in bk.readlines():
				if line.find('radius') != -1 and line.find('=') != -1:
					line = '%s%s\n' % (line[:line.find('=') + 2], self.tick_radius)
				if line.find('thickness') != -1 and line.find('=') != -1:
					line = '%s%s\n' % (line[:line.find('=') + 2], self.tick_thickness)
				if line.find('color') != -1 and line.find('=') != -1:
					line = '%s%s\n' % (line[:line.find('=') + 2], self.tick_color)
				if line.find('size') != -1 and line.find('=') != -1:
					line = '%s%s\n' % (line[:line.find('=') + 2], self.tick_size)
				ticksFile.write(line)
		ticksFile.close()
		os.remove(self.fullpath('ticks.conf.bk'))

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
		for i, circoslink in enumerate(self.circos_directed_links):
			currentFile = 'net{}.link.txt'.format(i)
			currentEnd = 'linkend{}.txt'.format(i)
			self.circosConfigFile.add_link(currentFile)
			self.circosConfigFile.add_direction(currentEnd)
			circoslink.write(self.fullpath(currentFile), self.fullpath(currentEnd))
		self.circosConfigFile.write(self.fullpath())
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
