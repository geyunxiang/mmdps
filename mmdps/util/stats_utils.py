"""
stats utils
"""
import numpy as np
import scipy, scipy.stats
from statsmodels.stats import multitest
from mmdps.proc import netattr

def row_wise_ttest(net1, net2, sigLevel = 0.05):
	"""
	This function performs row-wise t-test on two nets.
	The row, connections of one brain area, is considered to follow 
	some distribution. The 2 'groups' here are one row in net1 and the same
	row in net2.
	Note: the auto-correlation term is removed
	"""
	sigRegion = np.zeros(net1.data.shape[0])
	for rowIdx in range(net1.data.shape[0]):
		row1 = np.delete(net1.data[rowIdx, :], rowIdx)
		row2 = np.delete(net2.data[rowIdx, :], rowIdx)
		t, p = twoSampleTTest(row1, row2)
		if p < sigLevel:
			sigRegion[rowIdx] = 1
	return sigRegion

def mean_confidence_interval(data, confidence = 0.95):
	a = 1.0 * np.array(data)
	n = len(a)
	m, se = np.mean(a), scipy.stats.sem(a)
	h = se * scipy.stats.t.ppf((1+confidence)/2., n-1)
	return m, m-h, m+h

def twoSampleTTest(a, b):
	"""
	https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html
	"""
	t, p = scipy.stats.ttest_ind(a, b)
	return (t, p)

def non_parametric_two_sample_test(a, b):
	"""
	https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
	"""
	stat, p = scipy.stats.mannwhitneyu(a, b)
	return stat, p

def non_parametric_paired_test(a, b):
	"""
	https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
	"""
	stat, p = scipy.stats.wilcoxon(a, b)
	return stat, p

def pairedTTest(a, b):
	"""
	https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html
	"""
	t, p = scipy.stats.ttest_rel(a, b)
	return (t, p)

def permutation_test(a, b, num_rounds = 10000):
	"""
	http://rasbt.github.io/mlxtend/user_guide/evaluate/permutation_test/
	"""
	import mlxtend.evaluate
	p = mlxtend.evaluate.permutation_test(a, b, num_rounds = num_rounds, method = 'approximate')
	return (0, p)

def correlation_Pearson(a, b):
	pr, prp = scipy.stats.pearsonr(a, b)
	return pr, prp

def correlation_Spearman(a, b):
	sr, srp = scipy.stats.spearmanr(a, b)
	return sr, srp

def correlation_Kendall(a, b):
	tao, taop = scipy.stats.kendalltau(a, b)
	return tao, taop

def FDR_correction(p_list, sigLevel = 0.05):
	reject, pvals_corrected, _, _ = multitest.multipletests(p_list, sigLevel, method='fdr_bh')
	return reject, pvals_corrected

def bonferroni_correction(p_list, sigLevel = 0.05):
	reject, pvals_corrected, _, _ = multitest.multipletests(p_list, sigLevel, method='bonferroni')
	return reject, pvals_corrected

def filter_sigdiff_connections(netListA, netListB, sigLevel = 0.05, method = 'ttest', iterate_all = False):
	"""
	This function returns a list of significant different connections
	between two groups. The two groups can be a patient group and a 
	healthy control group. 
	This function takes in two lists of networks, perform 2 sample t-test or non-parametric tests on each 
	connections, and take out those that are significant.
	Connection is returned as a tuple of netattr.Connection. The first connection stores the t-val while the second connection stores p-val.
	If iterate_all, go over all connection pairs regardless of order. The connection returned is assumed to be directional. Otherwise only upper triangle part will be iterated
	"""
	ret = []
	atlasobj = netListA[0].atlasobj
	totalTests = 0
	if iterate_all:
		idx_iterator = atlasobj.iterate_idx_all()
	else:
		idx_iterator = atlasobj.iterate_idx()
	for xidx, yidx in idx_iterator:
		if method == 'ttest':
			# perform t-test
			t, p = scipy.stats.ttest_ind(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
		elif method == 'nonparametric':
			# perform Mann-Whitney U
			t, p = scipy.stats.mannwhitneyu(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
		else:
			raise Exception('Unknown comparison method: %s' % method)
		totalTests += 1
		if p < sigLevel:
			ret.append((netattr.Connection(atlasobj, xidx, yidx, t, directional = iterate_all), netattr.Connection(atlasobj, xidx, yidx, p, directional = iterate_all)))
	print('SigDiff connections: %d. Discover rate: %1.4f with sigLevel: %1.4f' % (len(ret), float(len(ret))/totalTests, sigLevel))
	return ret

def filter_sigdiff_connections_Bonferroni(netListA, netListB, sigLevel = 0.05):
	"""
	This function takes in two lists of networks, perform 2 sample t-test on each
	connections with Bonferroni correction (divide alpha by the number of tests).
	Specify the overall significance level in sigLevel
	"""
	region_num = netListA[0].atlasobj.count
	test_num = region_num*(region_num - 1)/2
	return filter_sigdiff_connections(netListA, netListB, float(sigLevel)/test_num)

def filter_sigdiff_connections_FDR(netListA, netListB, sigLevel = 0.05):
	"""
	This function performs 2 sample t-test on each connection using BH FDR correction.
	"""
	ret = []
	atlasobj = netListA[0].atlasobj
	totalTests = 0
	conn_p_list = [] # a list of tuples (xidx, yidx, 0.001) etc
	for xidx in range(atlasobj.count):
		for yidx in range(xidx + 1, atlasobj.count):
			# perform t-test
			t, p = scipy.stats.ttest_ind(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
			totalTests += 1
			conn_p_list.append((xidx, yidx, p))
	# FDR correction
	reject, pvals_corrected, _, _ = multitest.multipletests([a[2] for a in conn_p_list], sigLevel, method = 'fdr_bh')
	for idx in range(len(reject)):
		if reject[idx]:
			ret.append((conn_p_list[idx][0], conn_p_list[idx][1]))
	print('SigDiff connections: %d. Discover rate: %1.4f with sigLevel: %1.4f' % (len(ret), float(len(ret))/totalTests, sigLevel))
	return ret

def sigdiff_connections_after_treatment(netListA, netListB, sigLevel = 0.05, method = 'ttest', iterate_all = False):
	"""
	This function takes in two lists of networks, perform paired 1-sample t-test
	on each connections, and take out those that are significant.
	This function is used for the first and second scan of the same group to identify
	difference in FC after treatment.
	Connection is returned as a tuple of netattr.Connection. The first connection stores the t-val while the second connection stores p-val.
	If iterate_all, go over all connection pairs regardless of order. The connection returned is assumed to be directional. Otherwise only upper triangle part will be iterated
	"""
	ret = []
	atlasobj = netListA[0].atlasobj
	totalTests = 0
	if iterate_all:
		idx_iterator = atlasobj.iterate_idx_all()
	else:
		idx_iterator = atlasobj.iterate_idx()
	for xidx, yidx in idx_iterator:
		if method == 'ttest':
			# perform t-test
			t, p = scipy.stats.ttest_rel(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
		elif method == 'nonparametric':
			# perform Wilcoxon
			t, p = scipy.stats.wilcoxon(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
		else:
			raise Exception('Unknown comparison method: %s' % method)
		totalTests += 1
		if p < sigLevel:
			ret.append((netattr.Connection(atlasobj, xidx, yidx, t, directional = iterate_all), netattr.Connection(atlasobj, xidx, yidx, p, directional = iterate_all)))
	print('SigDiff connections: %d. Discover rate: %1.4f with sigLevel: %1.4f' % (len(ret), float(len(ret))/totalTests, sigLevel))
	return ret

def sigdiff_connections_after_treatment_FDR(netListA, netListB, sigLevel = 0.05):
	"""
	This function performs paired t-test on each connection using BH FDR correction
	"""
	ret = []
	atlasobj = netListA[0].atlasobj
	totalTests = 0
	conn_p_list = [] # a list of tuples (xidx, yidx, 0.001) etc
	for xidx in range(atlasobj.count):
		for yidx in range(xidx + 1, atlasobj.count):
			# perform t-test
			t, p = scipy.stats.ttest_rel(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
			totalTests += 1
			conn_p_list.append((xidx, yidx, p))
	# FDR correction
	reject, pvals_corrected, _, _ = multitest.multipletests([a[2] for a in conn_p_list], sigLevel, method = 'fdr_bh')
	for idx in range(len(reject)):
		if reject[idx]:
			ret.append((conn_p_list[idx][0], conn_p_list[idx][1]))
	print('SigDiff connections: %d. Discover rate: %1.4f with sigLevel: %1.4f' % (len(ret), float(len(ret))/totalTests, sigLevel))
	return ret

def connection_wise_test(netListA, netListB, method = 'ttest', iterate_all = False):
	"""
	This function compare each connection using data in netListA against netListB
	The comparison results, stat and pval, are stored in two netattr.Net and returned
	"""
	atlasobj = netListA[0].atlasobj
	stat_net = netattr.zero_net(atlasobj)
	pval_net = netattr.zero_net(atlasobj)
	if iterate_all:
		idx_iterator = atlasobj.iterate_idx_all()
	else:
		idx_iterator = atlasobj.iterate_idx()
	for xidx, yidx in idx_iterator:
		if method == 'ttest':
			# perform t-test
			t, p = scipy.stats.ttest_ind(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
		elif method == 'nonparametric':
			# perform Mann-Whitney U
			t, p = scipy.stats.mannwhitneyu(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
		else:
			raise ValueError(
				'Parameter comparison_method should be one of [\'ttest\', \'nonparametric\']. Given parameter value = %s' % method)
		stat_net.data[xidx, yidx] = t
		pval_net.data[xidx, yidx] = p
	return stat_net, pval_net

def get_sub_network_connections(sub_network_list, atlasobj):
	"""
	This function takes in a list of sub_network nodes and return all 
	connections (without auto-connections) within the sub_network
	"""
	ret = []
	for xnode in sub_network_list:
		for ynode in sub_network_list:
			ret.append((atlasobj.ticks.index(xnode), atlasobj.ticks.index(ynode)))
	return ret

def filter_sigdiff_connections_old(netListA, netListB, sigLevel = 0.05):
	"""
	this function takes in two lists of networks, perform 2 sample t-test on each 
	connections, and take out those that are significant. 
	The significant different connections are returned in a list of strings
	"""
	ret = []
	ticks = netListA[0].ticks
	totalTests = 0
	for xidx in range(len(ticks)):
		for yidx in range(xidx + 1, len(ticks)):
			t, p = scipy.stats.ttest_ind([a.get_value_at_idx(xidx, yidx) for a in netListA], 
				[b.get_value_at_idx(xidx, yidx) for b in netListB])
			totalTests += 1
			if p < sigLevel:
				ret.append('%s-%s' % (ticks[xidx], ticks[yidx]))
	print('SigDiff connections: %d. Discover rate: %1.4f with sigLevel: %1.4f' % (len(ret), float(len(ret))/totalTests, sigLevel))
	return ret
