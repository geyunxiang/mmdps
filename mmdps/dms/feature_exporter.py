"""
Export all features to feature database.

Use this exporter to export features from the calculation folder to feature database.
"""
import os
import shutil

from mmdps.util.loadsave import load_json_ordered, load_txt, load_csvmat
from mmdps.util import path
from mmdps.dms import mongodb_database
from mmdps.proc import netattr
from mmdps import rootconfig

class MRIScanProcMRIScanAtlasExporter:
	"""
	The feature exporter for mriscan processing.

	Only export for one mriscan and one atlas.
	"""
	def __init__(self, mriscan, atlasname, mainconfig, dataconfig, modal = None):
		"""Init the exporter."""
		self.mriscan = mriscan
		self.atlasname = atlasname
		self.mainconfig = mainconfig
		self.dataconfig = dataconfig
		self.output_root_folder = self.mainconfig['output_folder']
		self.input_folders = self.mainconfig['input_folders']
		self.modal = modal
		self.is_dynamic = self.dataconfig['dynamic']['is_dynamic']

	def fullinfolder(self, modal, *p):
		"""full file for input folder."""
		if self.atlasname:
			return os.path.join(self.input_folders[modal], self.mriscan, self.atlasname, *p)
		else:
			return os.path.join(self.input_folders[modal], self.mriscan, *p)

	def fulloutfolder(self, *p):
		"""full file for output folder."""
		if self.atlasname:
			return os.path.join(self.output_root_folder, self.mriscan, self.atlasname, *p)
		else:
			return os.path.join(self.output_root_folder, self.mriscan, *p)

	def get_dynamic_file_path(self, feature_config):
		modal = feature_config['modal']
		file_list = []
		out_file_list = []
		file_base = self.fullinfolder(modal, feature_config.get('file'))
		out_file_base = self.fulloutfolder(feature_config['out_file_name'])
		window_length = self.dataconfig['dynamic']['window_length']
		step_size = self.dataconfig['dynamic']['step_size']
		window_idx = 0
		while True:
			file_path = file_base + '_%d_%d' % (window_idx, window_idx + window_length) + feature_config.get('file_type')
			if not os.path.isfile(file_path):
				return file_list, out_file_list
			file_list.append(file_path)
			out_file_list.append(out_file_base + '_%d_%d' % (window_idx, window_idx + window_length) + feature_config.get('file_type'))
			window_idx += step_size

	def get_static_file_path(self, feature_config):
		modal = feature_config['modal']
		return [self.fullinfolder(modal, feature_config.get('file') + feature_config.get('file_type'))], [self.fulloutfolder(feature_config['out_file_name'] + feature_config.get('file_type'))]

	def get_feature_file_path(self, feature_config):
		modal = feature_config['modal']
		if self.modal is not None and modal != self.modal:
			return [], []
		if self.is_dynamic and modal == 'BOLD':
			# get dynamic files for BOLD
			return self.get_dynamic_file_path(feature_config)
		else:
			return self.get_static_file_path(feature_config)

	def run_feature(self, feature_name, feature_config):
		"""
		Export one feature.
		feature_name is used in sub-classes
		"""
		in_file_list, out_file_list = self.get_feature_file_path(feature_config)
		for file, filedst in zip(in_file_list, out_file_list):
			if not os.path.isfile(file):
				print('==Not Exist:', file)
				continue
			path.makedirs_file(filedst)
			#print('Copy:', file, filedst)
			shutil.copy2(file, filedst)

	def run(self):
		"""Export all features."""
		if self.atlasname:
			# atlased
			for netname, netconf in self.dataconfig['nets'].items():
				self.run_feature(netname, netconf)
			for attrname, attrconf in self.dataconfig['attrs'].items():
				self.run_feature(attrname, attrconf)
		else:
			# unatlased
			for filename, fileconf in self.dataconfig['unatlased'].items():
				self.run_feature(filename, fileconf)

class MRIScanProcMMDPDatabaseExporter(MRIScanProcMRIScanAtlasExporter):
	"""
	The feature exporter for mriscan processing. 
	Export features to MMDPDatabase (MongoDB Database)
	Only export for one mriscan and one atlas.
	"""
	def __init__(self, mriscan, atlasname, mainconfig, dataconfig, data_source, modal = None, force = False):
		"""
		If force == True, will overwrite existing features in the database
		"""
		super().__init__(mriscan, atlasname, mainconfig, dataconfig, modal)
		self.data_source = data_source
		self.mdb = mongodb_database.MongoDBDatabase(data_source)
		self.force = force

	def run_feature(self, feature_name, feature_config):
		"""
		Override super run_feature.
		Stores csv files to MongoDB directly
		"""
		if feature_config['file_type'] != '.csv':
			# only supports csv features
			return
		in_file_list, out_file_list = self.get_feature_file_path(feature_config)
		if self.is_dynamic and feature_config['modal'] == 'BOLD':
			if len(in_file_list) < 1:
				print('==Not Exist:', self.mriscan, self.atlasname, feature_name)
				return
			if feature_name.find('net') != -1:
				feature = netattr.DynamicNet(None, self.atlasname, self.dataconfig['dynamic']['window_length'], self.dataconfig['dynamic']['step_size'], scan = self.mriscan, feature_name = feature_name)
				for file in in_file_list:
					feature.append_one_slice(load_csvmat(file))
				try:
					self.mdb.save_dynamic_network(feature)
				except mongodb_database.MultipleRecordException:
					if self.force:
						# delete and overwrite
						self.mdb.remove_dynamic_network(self.mriscan, self.dataconfig['dynamic']['window_length'], self.dataconfig['dynamic']['step_size'], self.atlasname)
						self.mdb.save_dynamic_network(feature)
					else:
						print('!!!Already Exist: %s %s %s. Skipped' % (self.mriscan, self.atlasname, feature_name))
			else:
				feature = netattr.DynamicAttr(None, self.atlasname, self.dataconfig['dynamic']['window_length'], self.dataconfig['dynamic']['step_size'], scan = self.mriscan, feature_name = feature_name)
				for file in in_file_list:
					feature.append_one_slice(load_csvmat(file))
				try:
					self.mdb.save_dynamic_attr(feature)
				except mongodb_database.MultipleRecordException:
					if self.force:
						# delete and overwrite
						self.mdb.remove_dynamic_attr(self.mriscan, feature_name, self.dataconfig['dynamic']['window_length'], self.dataconfig['dynamic']['step_size'], self.atlasname)
						self.mdb.save_dynamic_attr(feature)
					else:
						print('!!!Already Exist: %s %s %s. Skipped' % (self.mriscan, self.atlasname, feature_name))
		elif self.is_dynamic:
			# dynamic but not BOLD feature
			return
		else:
			# not dynamic
			for file in in_file_list:
				if not os.path.isfile(file):
					print('==Not Exist:', self.mriscan, self.atlasname, feature_name)
					continue
				if feature_name.find('net') != -1:
					feature = netattr.Net(load_csvmat(file), self.atlasname, self.mriscan, feature_name)
				else:
					feature = netattr.Attr(load_csvmat(file), self.atlasname, self.mriscan, feature_name)
				try:
					self.mdb.save_static_feature(feature)
				except mongodb_database.MultipleRecordException:
					if self.force:
						# delete and overwrite
						self.mdb.remove_static_feature(self.mriscan, self.atlasname, feature_name)
						self.mdb.save_static_feature(feature)
					else:
						print('!!!Already Exist: %s %s %s. Skipped' % (self.mriscan, self.atlasname, feature_name))

class MRIScanProcExporter:
	"""
	The feature exporter.

	Export features in all mriscans.
	"""
	def __init__(self, mainconfig, dataconfig, modal = None, database = False, data_source = None, force = False):
		"""Init the exporter using mainconfig and dataconfig."""
		self.mainconfig = mainconfig
		self.dataconfig = dataconfig
		if mainconfig.get('atlas_list', None) is None or mainconfig.get('atlas_list', None) == 'all':
			# use default atlas_list
			self.atlas_list = load_txt(os.path.join(rootconfig.path.atlas, 'atlas_list.txt'))
		elif type(mainconfig['atlas_list']) is list:
			self.atlas_list = mainconfig['atlas_list']
		else:
			self.atlas_list = load_txt(mainconfig['atlas_list'])
		if os.path.isfile(mainconfig['scan_list']):
			self.mriscans = load_txt(mainconfig['scan_list'])
		elif mainconfig['scan_list'] == 'listdir':
			if modal is not None:
				self.mriscans = sorted(os.listdir(mainconfig['input_folders'][modal]))
			else:
				self.mriscans = sorted(os.listdir(mainconfig['input_folders']['T1']))
		else:
			raise Exception('Unrecognized scan_list:', mainconfig['scan_list'])
		self.modal = modal
		self.database = database
		self.data_source = data_source
		self.force = force

	def run_mriscan_atlas(self, mriscan, atlasname):
		"""Run one mriscan and one atlas to export."""
		if not self.database:
			atlas_exporter = MRIScanProcMRIScanAtlasExporter(mriscan, atlasname, self.mainconfig, self.dataconfig, self.modal)
		else:
			atlas_exporter = MRIScanProcMMDPDatabaseExporter(mriscan, atlasname, self.mainconfig, self.dataconfig, self.data_source, self.modal, self.force)
		atlas_exporter.run()

	def run(self):
		"""Run the export."""
		for atlasname in self.atlas_list:
			# atlased
			for mriscan in self.mriscans:
				self.run_mriscan_atlas(mriscan, atlasname)
		if 'unatlased' in self.dataconfig:
			# unatlased
			for mriscan in self.mriscans:
				self.run_mriscan_atlas(mriscan, None)

def check_modal(modal, mainconfigfile):
	mainconfig = load_json_ordered(mainconfigfile)
	if modal not in mainconfig['input_folders'].keys():
		raise Exception('modal %s not valid (%s)' % (modal, list(mainconfig['input_folders'].keys())))

def create_by_files(mainconfigfile, dataconfigfile):
	"""Create exporter by config files."""
	mainconfig = load_json_ordered(mainconfigfile)
	dataconfig = load_json_ordered(dataconfigfile)
	return MRIScanProcExporter(mainconfig, dataconfig)

def create_by_folder(atlasobj, configsfolder):
	"""Create exporter by folder, which should includes the config files."""
	mainconfigfile = os.path.join(configsfolder, 'export_mainconf.json')
	dataconfigfile = os.path.join(configsfolder, 'export_dataconf.json')
	return create_by_files(mainconfigfile, dataconfigfile)
