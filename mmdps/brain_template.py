import os
import json
from mmdps import brain_net
from mmdps.loadfile import load_json

folder_module = os.path.dirname(os.path.abspath(__file__))

class BrainTemplate:
	def __init__(self, config):
		self.config = config
		self.name = self.config['name']
		self.nii_path = os.path.abspath(os.path.join(folder_module, '../data/templates/%s.nii' % self.name))
		self.brief = self.config['brief']
		self.numRegions = self.config['count']
		self.count = self.numRegions
		self.regions = self.config['regions'] # actual number in nii file
		self.ticks = self.config['ticks']
		self.plotindexes = self.config['plotindexes'] # plot which first
		if 'nodefile' in self.config:
			self.nodefile = brain_net.get_nodefile(self.config['nodefile'])
		self.ticks_adjusted = self.adjust_ticks()
		if 'volumes' in self.config:
			self.add_volumes(self.config['volumes'])

	def add_volumes(self, volumes):
		self.volumes = {}
		for volumename in volumes:
			self.volumes[volumename] = volumes[volumename]

	def get_volume(self, volumename):
		return self.volumes[volumename]

	def adjust_ticks(self):
		adjticks = [None] * self.numRegions
		for i in range(self.numRegions):
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

	def ticks_to_plot_indexes(self, ticks):
		"""
		return the plot indexes for the given ticks defined by this template
		"""
		return [self.plotindexes[self.ticks.index(tick)] for tick in ticks]

	def ticks_to_indexes(self, ticks):
		return [self.ticks.index(tick) for tick in ticks]

def get_template(template_name):
	template_folder = os.path.join(folder_module, '../data/templates')
	template_folder = os.path.abspath(template_folder)
	config_file = template_name + '.json'
	config_file_path = os.path.join(template_folder, config_file)
	template_config = load_json(config_file_path)
	return BrainTemplate(template_config)

def load_template(folder, templatename):
	config_file_path = os.path.join(folder, templatename + '.json')
	templatedesc = load_json(config_file_path)
	templatedesc['nodefile'] = os.path.join(folder, templatedesc['nodefile'])
	return BrainTemplate(templatedesc)

if __name__ == '__main__':
	t = get_template('aal')
	print(t)
