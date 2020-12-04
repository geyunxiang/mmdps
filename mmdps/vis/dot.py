import os
import numpy as np
from graphviz import Digraph

def plot_local_digraph(net, nodeIdx, savepath):
	"""
	Plot local networks related to nodeIdx
	The net should be a (binary) square matrix, not necessarily symmetric however.
	All paths related to nodeIdx will be plotted
	"""
	os.makedirs(os.path.join(os.path.dirname(savepath), 'dotdata'), exist_ok = True)
	atlasobj = net.atlasobj
	# will save to graph_name.gv and graph_name.gv.png
	graph_name = os.path.splitext(os.path.basename(savepath))[0]
	graph = Digraph(name = graph_name, format = 'png', engine = 'dot', directory = os.path.join(os.path.dirname(savepath), 'dotdata'))
	graph.attr('graph', dpi = '300')
	# graph.attr('node', shape = 'circle', fixedsize = 'True')
	graph.attr('node', shape = 'box')
	graph.node(atlasobj.ticks[nodeIdx], atlasobj.ticks[nodeIdx] + '\n' + atlasobj.region_names[nodeIdx], style = 'filled', fillcolor = 'turquoise')
	row_idx, column_idx = np.nonzero(net.data)
	for r, c in zip(row_idx, column_idx):
		graph.node(atlasobj.ticks[r], atlasobj.ticks[r] + '\n' + atlasobj.region_names[r])
		graph.node(atlasobj.ticks[c], atlasobj.ticks[c] + '\n' + atlasobj.region_names[c])
		if atlasobj.ticks[r][0] != atlasobj.ticks[c][0]:
			# L2 -> R6 etc
			graph.edge(atlasobj.ticks[r], atlasobj.ticks[c], color = 'red')
		else:
			graph.edge(atlasobj.ticks[r], atlasobj.ticks[c])
	graph.render()
	if os.path.exists(os.path.join(os.path.dirname(savepath), graph_name + '.png')):
		os.remove(os.path.join(os.path.dirname(savepath), graph_name + '.png'))
	os.rename(os.path.join(os.path.dirname(savepath), 'dotdata', graph_name + '.gv.png'), os.path.join(os.path.dirname(savepath), graph_name + '.png'))

if __name__ == '__main__':
	# test script
	from mmdps.proc import netattr, atlas
	atlasobj = atlas.get('brodmann_lr')
	net = netattr.Net(np.zeros((atlasobj.count, atlasobj.count)), atlasobj)
	net.data[0, 2] = 1
	net.data[4, 0] = 1
	net.data[8, 4] = 1
	net.data[65, 0] = 1
	plot_local_digraph(net, 0, 'E:/Results/test.png')
