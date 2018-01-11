import os
import json
from mmdps import BrainNet
from mmdps.loadfile import load_json

folder_module = os.path.dirname(os.path.abspath(__file__))

class BrainTemplate:
	def __init__(self, descdict):
		self.dd = descdict
		self.name = self.dd['name']
		self.brief = self.dd['brief']
		self.count = self.dd['count']
		self.regions = self.dd['regions']
		self.ticks = self.dd['ticks']
		self.plotindexes = self.dd['plotindexes']
		if 'nodefile' in self.dd:
			self.nodefile = BrainNet.get_nodefile(self.dd['nodefile'])
		self.ticks_adjusted = self.adjust_ticks()
		if 'volumes' in self.dd:
			self.add_volumes(self.dd['volumes'])

	def add_volumes(self, volumes):
		self.volumes = {}
		for volumename in volumes:
			self.volumes[volumename] = volumes[volumename]

	def get_volume(self, volumename):
		return self.volumes[volumename]

	def adjust_ticks(self):
		adjticks = [None] * self.count
		for i in range(self.count):
			realpos = self.plotindexes[i]
			adjticks[i] = self.ticks[realpos]
		return adjticks

	def ticks_to_regions(self, ticks):
		if not hasattr(self, '_tickregiondict'):
			self._tickregiondict = dict([(k, v) for k, v in zip(self.ticks, self.regions)])
		regions = [self._tickregiondict[tick] for tick in ticks]
		return regions

	def regions_to_indexes(self, regions):
		if not hasattr(self, '_regionindexdict'):
			self._regionindexdict = dict([(k, i) for i, k in enumerate(self.regions)])
		indexes = [self._regionindexdict[region] for region in regions]
		return indexes

	def ticks_to_indexes(self, ticks):
		if not hasattr(self, '_tickindexdict'):
			self._tickindexdict = dict([(k, i) for i, k in enumerate(self.ticks)])
		indexes = [self._tickindexdict[tick] for tick in ticks]
		return indexes

def get_template(name):
	folder_templates = os.path.join(folder_module, '../../../data/templates')
	folder_templates = os.path.abspath(folder_templates)
	jfilename = name+'.json'
	jfilepath = os.path.join(folder_templates, jfilename)
	tconf = load_json(jfilepath)
	return BrainTemplate(tconf)

def load_template(folder, templatename):
	jfilepath = os.path.join(folder, templatename + '.json')
	templatedesc = load_json(jfilepath)
	templatedesc['nodefile'] = os.path.join(folder, templatedesc['nodefile'])
	return BrainTemplate(templatedesc)

if __name__ == '__main__':
	t = get_template('aal')
	print(t)
