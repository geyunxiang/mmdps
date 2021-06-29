import multiprocessing
import queue

import numpy as np
from mmdps.util import stats_utils
from mmdps.proc import netattr, parabase

def NBS_permutation_meta(args):
	network_list = args['network']
	group_size = args['group']
	stat_thresh = args.get('stat_thresh', None)
	pval_thresh = args.get('pval_thresh', None)
	comparison_method = args.get('comparison_method', 'ttest')
	cc_method = args.get('cc_method', 'simple')
	directed = args.get('directed', False)
	perm = np.random.permutation(len(network_list))
	network_list_1 = [network_list[perm[idx]] for idx in range(group_size)]
	network_list_2 = [network_list[perm[idx]] for idx in range(group_size, len(network_list))]
	stat_net, pval_net = stats_utils.connection_wise_test(network_list_1, network_list_2, iterate_all = directed, method = comparison_method)
	if stat_thresh is not None:
		sig_conn_net = stat_net.binarize(stat_thresh)
	elif pval_thresh is not None:
		sig_conn_net = pval_net.binarize(pval_thresh, True)
	else:
		raise ValueError('Input at least one of stat_thresh and pval_thresh')
	if cc_method == 'simple':
		if directed:
			sig_conn_net.data = ((sig_conn_net.data + np.transpose(sig_conn_net.data)) > 0).astype(int)
		_, max_size = sig_conn_net.connected_components()
	elif cc_method == 'scc':
		if not directed:
			raise ValueError('cc_method \'scc\' only supports directed network')
		dir_net = netattr.DirectedNet(sig_conn_net.data, sig_conn_net.atlasobj)
		_, max_size = dir_net.connected_components()
	else:
		raise ValueError(
			'Parameter cc_method should be one of [\'simple\', \'scc\']. Given parameter value = %s' % cc_method)
	return max_size

def NBS_component_parallel(network_list_1, network_list_2, directed, comparison_method, threshold, cc_method='simple', permutation_num=5000, sig_level=0.05, parallel_num = 4):
	"""
	Perform permutation test in parallel. Test for significant network topology between the two network lists
	:param parallel_num: Number of parallel workers
	:param directed: True or False
	:param threshold: A dict containing 'pval_thresh' or 'stat_thresh'
	:param comparison_method: 'ttest' or 'nonparametric'
	:param network_list_1: First network list
	:param network_list_2: Second network list
	:param cc_method: Methods to identify connected components. simple: treat directed network as undirected network. scc: select strongly connected components
	:param permutation_num: How many times to permute
	:param sig_level: Final controlled significance level
	:return: A list of tuple (cc_sig, emp_pval). cc_sig is a list of node indices and emp_pval is the empirical p-value
	"""
	result = []
	# 1. Get connection-wise comparison result
	stat_net, pval_net = stats_utils.connection_wise_test(network_list_1, network_list_2, iterate_all=directed, method = comparison_method)
	# 2. Apply threshold to result network
	stat_thresh = threshold.get('stat_thresh', None)
	pval_thresh = threshold.get('pval_thresh', None)
	if stat_thresh is not None:
		sig_conn_net = stat_net.binarize(stat_thresh)
	elif pval_thresh is not None:
		sig_conn_net = pval_net.binarize(pval_thresh, True)
	else:
		raise ValueError('Parameter threshold should be a dict containing at least one of [\'stat_thresh\', \'pval_thresh\']. Given parameter value = %s' % threshold)
	# 3. Find connected components for sig_conn_net
	if cc_method == 'simple':
		# 3.1 Simplify directed network to undirected network
		if directed:
			sig_conn_net.data = ((sig_conn_net.data + np.transpose(sig_conn_net.data)) > 0).astype(int)
		cc_sig, max_size = sig_conn_net.connected_components()
	elif cc_method == 'scc':
		if not directed:
			raise ValueError('cc_method \'scc\' only supports directed network')
		# 3.2 Select strongly connected components
		dir_net = netattr.DirectedNet(sig_conn_net.data, sig_conn_net.atlasobj)
		cc_sig, max_size = dir_net.connected_components()
	else:
		raise ValueError(
			'Parameter cc_method should be one of [\'simple\', \'scc\']. Given parameter value = %s' % cc_method)
	# 4. Generate empirical null distribution by permutation test
	empirical = [0] * permutation_num # stores maximum component size
	perm_idx = 0
	network_list = network_list_1 + network_list_2
	num_1 = len(network_list_1)

	pool = multiprocessing.Pool(processes = parallel_num)
	manager = multiprocessing.Manager()
	managerQueue = manager.Queue()
	fwrap = parabase.FWrap(NBS_permutation_meta, managerQueue)
	pool_result = pool.map_async(fwrap.run, [dict(network = network_list, group = num_1, directed = directed, stat_thresh = stat_thresh, pval_thresh = pval_thresh, cc_method = cc_method, comparison_method = comparison_method)] * permutation_num)
	while True:
		if pool_result.ready():
			break
		else:
			try:
				res = managerQueue.get(timeout=1)
				empirical[perm_idx] = res['res']
				# print('res = ', res['res'])
			except queue.Empty:
				continue
			else:
				perm_idx += 1
				print('%s, %s, %s, pval_thresh = %1.4f, Permutation %d/%d' % (directed, comparison_method, cc_method, pval_thresh, perm_idx, permutation_num))
	print('End proc')
	# result.append(pool_result.get())
	pool.close()
	pool.join()
	assert(perm_idx == permutation_num)
	# 5. Decide whether connected components are significant
	print(cc_sig, max_size)
	for cc in cc_sig:
		emp_pval = sum(i >= len(cc) for i in empirical)/float(permutation_num)
		if emp_pval < sig_level:
			result.append((cc, emp_pval))
	return dict(cc_sig = cc_sig, empirical = empirical, result = result)
