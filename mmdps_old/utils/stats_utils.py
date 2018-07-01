"""
stats utils
"""
import numpy as np
import scipy, scipy.stats
from sklearn import svm

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

def filter_sigdiff_connections(netListA, netListB, sigLevel = 0.05):
	"""
	This function is an implementation on the new mmdps version
	A connection is represented by a 2-element-tuple of idx
	"""
	ret = []
	atlasobj = netListA[0].atlasobj
	totalTests = 0
	for xidx in range(atlasobj.count):
		for yidx in range(xidx + 1, atlasobj.count):
			# perform t-test
			t, p = scipy.stats.ttest_ind(
				[a.data[xidx, yidx] for a in netListA], 
				[b.data[xidx, yidx] for b in netListB])
			totalTests += 1
			if p < sigLevel:
				ret.append((xidx, yidx))
	print('SigDiff connections: %d. Discover rate: %1.4f with sigLevel: %1.4f' % (len(ret), float(len(ret))/totalTests, sigLevel))
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