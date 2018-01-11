import json
import os.path
from . import BrainNet

folder_module = os.path.dirname(os.path.abspath(__file__))

class BrainTemplate:
	def __init__(self, descdict, niipath=None):
		self.dd = descdict
		self.niipath = niipath
		self.name = self.dd['name']
		self.brief = self.dd['brief']
		self.count = self.dd['count']
		self.regions = self.dd['regions']
		self.ticks = self.dd['ticks']
		self.plotindexes = self.dd['plotindexes']
		self.region_counts = self.dd['region_counts']
		if 'nodefile' in self.dd:
			self.nodefilename = self.dd['nodefile']
			self.nodefile = BrainNet.get_nodefile(self.nodefilename)
		self.ticks_adjusted = self.adjust_ticks()
		
	def __str__(self):
		return 'BrainTemplate: ' + self.name + ' ' + self.niipath

	def adjust_ticks(self):
		adjticks = [None] * self.count
		for i in range(self.count):
			realpos = self.plotindexes[i]
			adjticks[i] = self.ticks[realpos]
		return adjticks

	def ticks_to_regions(self, ticks):
		allticks = self.ticks
		allregions = self.regions
		tickregiondict = dict([(k, v) for k, v in zip(allticks, allregions)])
		regions = [tickregiondict[tick] for tick in ticks]
		return regions

	def regions_to_indexes(self, regions):
		regionindexdict = dict([(k, i) for i, k in enumerate(self.regions)])
		indexes = [regionindexdict[region] for region in regions]
		return indexes
	
	def ticks_to_indexes(self, ticks):
		tickindexdict = dict([(k, i) for i, k in enumerate(self.ticks)])
		indexes = [tickindexdict[tick] for tick in ticks]
		return indexes

def get_template(name):
	folder_templates = os.path.join(folder_module, '../../../data/templates')
	folder_templates = os.path.abspath(folder_templates)
	jfilename = name+'.json'
	niifilename = name+'.nii'
	jfile = os.path.join(folder_templates, jfilename)
	niifile = os.path.join(folder_templates, niifilename)
	with open(jfile) as f:
		t = json.load(f)
	template = BrainTemplate(t, niifile)
	return template

def get_template_json(jfullpath, niifullpath):
	with open(jfullpath) as f:
		t = json.load(f)
	template = BrainTemplate(t)
	return template

if __name__ == '__main__':
	#t = get_template('brodmann_lr_3')
	t = get_template('aal_1')
	print(t)
	print(t.name)
	print(t.regions)
	
	
	
