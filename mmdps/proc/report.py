"""
Analysis and Report
"""

from mmdps.proc import loader, netattr

class GroupAnalysisAssistant():
	"""docstring for GroupAnalysisAssistant"""
	def __init__(self, study):
		self.study = study

	def compare_BOLD_attrs(self):
		pass
		
	def plot_BOLD_attr_line(self):
		pass

	def plot_BOLD_attr_BNV(self):
		pass

	def compare_BOLD_networks(self, atlasobj, group1_name, group2_name, comparison_method):
		group1 = self.study.getGroupContainingName(group1_name)
		group2 = self.study.getGroupContainingName(group2_name)
		group1_nets = [loader.load_network(atlasobj, scan_table.filename) for scan_table in group1.scans]
		group2_nets = [loader.load_network(atlasobj, scan_table.filename) for scan_table in group2.scans]
		stats_network, p_network = netattr.networks_comparisons(group2_nets, group1_nets, comparison_method)
		return stats_network, p_network

	def plot_BOLD_network_circos(self):
		pass

class SingleAnalysisAssistant():
	"""docstring"""
	def __init__(self, name):
		self.subjectName = name

	def plot_BOLD_attr_line(self):
		pass
