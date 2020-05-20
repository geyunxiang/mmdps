"""
Analysis and Report
"""

from mmdps.proc import loader, netattr
from mmdps.dms import mmdpdb, tables
from mmdps.vis import line

class GroupAnalysisAssistant():
	"""docstring for GroupAnalysisAssistant"""
	def __init__(self, study_name, atlasobj):
		"""
		Specify study_name and the assistant will load a ResearchStudy instance, 
		as well as storing the session in order to avoid sqlalchemy.orm.exc.DetachedInstanceError
		self.group_nets stores networks of a group in a dict, with key = group name
		"""
		db = mmdpdb.MMDPDatabase()
		self.session = db.new_session()
		self.study = self.session.query(tables.ResearchStudy).filter_by(alias = study_name).one()
		self.atlasobj = atlasobj
		self.group_nets = dict()
		self.attr_comparison_result = dict()

	def compare_BOLD_attrs(self, group1_name, group2_name, comparison_method, plotting = False):
		"""
		comparison is performed by group2 - group1
		comparison_method should be one of stats_utils.pairedTTest or stats_utils.twoSampleTTest
		"""
		group1_attr_list = loader.load_attrs(self.study.getGroup(group1_name).getScanStrList())
		group1_attr_mean = netattr.averageAttr(group1_attr_list)
		group1_attr_mean.scan = '%s mean' % group1_name

		group2_attr_list = loader.load_attrs(self.study.getGroup(group2_name).getScanStrList())
		group2_attr_mean = netattr.averageAttr(group2_attr_list)
		group2_attr_mean.scan = '%s mean' % group2_name

		t_attr, p_attr = netattr.attr_comparisons(group2_attr_list, group1_attr_list, comparison_method)

		for idx in range(self.atlasobj.count):
			if p_attr.data[idx] < 0.05:
				print('tick: %s t = %1.4f, p = %1.4f' % (self.atlasobj.ticks[idx], t_attr.data[idx], p_attr.data[idx]))
		self.attr_comparison_result['%s vs %s' % (group1_name, group2_name)] = dict(t_attr = t_attr, p_attr = p_attr, group1_attr_mean = group1_attr_mean, group2_attr_mean = group2_attr_mean)
		return t_attr, p_attr

	def compare_BOLD_networks(self, group1_name, group2_name, comparison_method):
		group1 = self.study.getGroup(group1_name)
		group2 = self.study.getGroup(group2_name)
		self.group_nets[group1.name] = [loader.load_single_network(self.atlasobj, scan_table.filename) for scan_table in group1.scans]
		self.group_nets[group2.name] = [loader.load_single_network(self.atlasobj, scan_table.filename) for scan_table in group2.scans]
		stats_network, comp_p_network = netattr.networks_comparisons(self.group_nets[group2.name], self.group_nets[group1.name], comparison_method)
		return stats_network, comp_p_network

	def correlate_sigdiff_BOLD_network(self, group1_name, group2_name, scoreLoader, score1_name, score2_name, comp_p_network, correlation_method):
		"""
		Only significant different connections will be correlated to scores.
		Correlation coefficient and p_vals of significant correlated links will be stored to r_network and corr_p_network
		"""
		group1 = self.study.getGroup(group1_name)
		group2 = self.study.getGroup(group2_name)
		r_network = netattr.zero_net(self.atlasobj)
		corr_p_network = netattr.one_net(self.atlasobj)
		for xidx in range(self.atlasobj.count):
			for yidx in range(xidx, self.atlasobj.count):
				if comp_p_network.data[xidx, yidx] > 0.05:
					continue
				FC_list = [net.data[xidx, yidx] for net in self.group_nets[group1.name]] + [net.data[xidx, yidx] for net in self.group_nets[group2.name]]
				score_list = [scoreLoader[subject][score1_name] for subject in group1.getSubjectNameList()] + [scoreLoader[subject][score2_name] for subject in group2.getSubjectNameList()]
				r, p = correlation_method(FC_list, score_list)
				if p < 0.05:
					r_network.data[xidx, yidx] = r
					r_network.data[yidx, xidx] = r
					corr_p_network.data[xidx, yidx] = p
					corr_p_network.data[yidx, xidx] = p
		return r_network, corr_p_network

	def generate_result_comp(self, stats_network, comp_p_network):
		result_list = []
		for xidx, xtick in enumerate(self.atlasobj.ticks):
			for yidx in range(xidx, self.atlasobj.count):
				ytick = self.atlasobj.ticks[yidx]
				if comp_p_network.data[xidx, yidx] < 0.05:
					result_list.append(dict(area1 = xtick, area2 = ytick, stat = stats_network.data[xidx, yidx], p_val = comp_p_network.data[xidx, yidx]))
		return result_list

	def generate_result_comp_corr(self, stats_network, comp_p_network, r_network, corr_p_network):
		result_list = []
		for xidx, xtick in enumerate(self.atlasobj.ticks):
			for yidx in range(xidx, self.atlasobj.count):
				ytick = self.atlasobj.ticks[yidx]
				if comp_p_network.data[xidx, yidx] < 0.05 and corr_p_network.data[xidx, yidx] < 0.05:
					result_list.append(dict(area1 = xtick, area2 = ytick, stat = stats_network.data[xidx, yidx], p_val = comp_p_network.data[xidx, yidx], corr_r = r_network.data[xidx, yidx], corr_p = corr_p_network.data[xidx, yidx]))
		return result_list

	def plot_BOLD_attr_line(self, group1_name, group2_name, title, outfilepath):
		comparison_key = '%s vs %s' % (group1_name, group2_name)
		if comparison_key not in self.attr_comparison_result:
			raise Exception('%s vs %s not analyzed' % (group1_name, group2_name))
		group1_attr_mean = self.attr_comparison_result[comparison_key]['group1_attr_mean']
		group2_attr_mean = self.attr_comparison_result[comparison_key]['group2_attr_mean']
		p_attr = self.attr_comparison_result[comparison_key]['p_attr']
		t_attr = self.attr_comparison_result[comparison_key]['t_attr']
		line.plot_attr_lines([group1_attr_mean, group2_attr_mean], title = title, outfilepath = outfilepath, sig_positions = (p_attr.data<0.05).astype(int), stat_list = zip(t_attr.data, p_attr.data))

	def plot_BOLD_attr_BNV(self):
		pass

	def plot_BOLD_network_circos(self):
		pass

class SingleAnalysisAssistant():
	"""docstring"""
	def __init__(self, name):
		self.subjectName = name

	def plot_BOLD_attr_line(self):
		pass
