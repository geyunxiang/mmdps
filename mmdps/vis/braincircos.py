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
	def __init__(self, net, threshold=0.6, valuerange=(-1,1)):
		self.net = net
		self.threshold = threshold
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

	def get_rowcol(self, chrA, idxA, chrB, idxB):
		row = chrA.indexes[idxA]
		col = chrB.indexes[idxB]
		return (row, col)

	def get_value(self, chrA, idxA, chrB, idxB):
		row, col = self.get_rowcol(chrA, idxA, chrB, idxB)
		bmask = self.mask[row, col]
		if bmask:
			return self.data[row, col]
		else:
			return None

	def get_cmap(self):
		return cm.coolwarm

	def map_value(self, value):
		valuerange = self.valuerange
		a = valuerange[0]
		b = valuerange[1]
		return (value-a) / (b-a)

	def get_color(self, chrA, idxA, chrB, idxB):
		value = self.get_value(chrA, idxA, chrB, idxB)
		if value is None:
			return None
		else:
			value = self.map_value(value)
			color = self.get_cmap()(value, bytes=True)
			return color

	def get_line(self, chrA, idxA, chrB, idxB):
		linkfmt = '{} {} {} {} {} {} {}'  # L_1 0 1 L_1 1 2 color=(10,10,10)
		color = self.get_color(chrA, idxA, chrB, idxB)
		if color is None:
			return None
		else:
			colorstr = color_to_str(color)
			linkline = linkfmt.format(*chrA.bandtuples[idxA], *chrB.bandtuples[idxB], colorstr)
			return linkline

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
	def __init__(self, attr, valuerange = None):
		self.brainparts = attr.atlasobj.get_brainparts()
		if valuerange is None:
			self.valuerange = (np.min(attr.data), np.max(attr.data))
		else:
			self.valuerange = valuerange
		self.chrdict = self.brainparts.chrdict
		self.attr = attr
		self.data = self.attr.data

	def get_index(self, chro, idx):
		return chro.indexes[idx]
	
	def get_value(self, chro, idx):
		return self.data[self.get_index(chro, idx)]

	def get_cmap(self):
		return cm.Reds
	
	def get_color(self, chro, idx):
		value = self.get_value(chro, idx)
		value = self.map_value(value)
		color = self.get_cmap()(value, bytes=True)
		return color
	
	def map_value(self, value):
		valuerange = self.valuerange
		a = valuerange[0]
		b = valuerange[1]
		return (value-a) / (b-a)
	
	def get_line(self, chro, idx):
		valuefmt = '{} {} {} {} {}'  # L_1 0 1 0.312 color=(10,10,10)
		value = self.get_value(chro, idx)
		color = self.get_color(chro, idx)
		colorstr = color_to_str(color)
		valueline = valuefmt.format(*chro.bandtuples[idx], value, colorstr)
		return valueline
	
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

	def customizeSize(self, ideogram_radius, label_size, linkThickness = None):
		"""
		input ideogram_radius as a string like '0.80'
			- ideogram_radius controls the size of the whole ring
		input label_size as a string like '40p'
			- label_size controls the font size of the ticks (L1, R2 etc.)
		input linkThickness as an integer like 20
			- linkThickness controls the thickness of network links(edges)
		"""
		self.customizedSizes = True
		self.radius = ideogram_radius
		self.circosConfigFile.customizeSize(label_size, linkThickness)

	def fullpath(self, *p):
		return os.path.join(self.circosfolder, *p)

	def add_circosvalue(self, circosvalue):
		self.circosvalues.append(circosvalue)

	def add_circoslink(self, circoslink):
		self.circoslinks.append(circoslink)

	def get_colorlist(self):
		return ['grey'] * self.atlasobj.count

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

	def run_circos(self):
		j = job.ExecutableJob('circos', rootconfig.path.circos, wd=self.fullpath())
		j.run()
		generatedpng = self.fullpath('circos.png')
		if os.path.isfile(generatedpng):
			finalpng = self.decorate_figure(generatedpng)
			shutil.copy2(finalpng, self.outfilepath + '.png')

	def get_title(self):
		return self.title

	def decorate_figure(self, generatedpng):
		img = Image.open(generatedpng)
		padtop = 100
		imgn = Image.new('RGBA', (img.width, padtop + img.height), (255, 255, 255, 255))
		imgn.paste(img, (0, padtop, img.width, padtop + img.height))
		draw = ImageDraw.Draw(imgn)
		font = ImageFont.truetype('arial.ttf', 72)
		draw.text((50, 50), self.get_title(), (0, 0, 0), font=font)
		newpng = generatedpng[:-4] + '_decorated.png'
		imgn.save(newpng)
		return newpng

	def plot(self):
		self.copy_files()
		self.write_files()
		self.run_circos()

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
