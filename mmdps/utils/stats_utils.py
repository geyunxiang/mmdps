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

def filter_sigdiff_connections(netListA, netListB):
	"""
	this function takes in two lists of networks, perform 2 sample t-test on each 
	connections, and take out those that are significant. The significant different
	connections are returned in two matrix (n_sample, n_sig). 
	"""
	