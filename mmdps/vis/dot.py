import os
import numpy as np
from graphviz import Digraph

def plot_whole_digraph(net, savepath, color_scheme = {}):
	"""
	Input color_scheme as tick: fillcolor
	See https://graphviz.org/doc/info/attrs.html#k:color
	Colors can be specified using one of four formats:
		"#%2x%2x%2x" 	Red-Green-Blue (RGB)
		"#%2x%2x%2x%2x" 	Red-Green-Blue-Alpha (RGBA)
		"H[, ]+S[, ]+V" 	Hue-Saturation-Value (HSV) 0.0 <= H,S,V <= 1.0
		string 	color name
		Color 		RGB 		HSV 					String
		White 		"#ffffff" 	"0.000 0.000 1.000" 	"white"
		Black 		"#000000" 	"0.000 0.000 0.000" 	"black"
		Red 		"#ff0000" 	"0.000 1.000 1.000" 	"red"
		Turquoise 	"#40e0d0" 	"0.482 0.714 0.878" 	"turquoise"
		Sienna 		"#a0522d" 	"0.051 0.718 0.627" 	"sienna"
	"""
	default_fillcolor = 'white'
	os.makedirs(os.path.join(os.path.dirname(savepath), 'dotdata'), exist_ok = True)
	atlasobj = net.atlasobj
	# will save to graph_name.gv and graph_name.gv.png
	graph_name = os.path.splitext(os.path.basename(savepath))[0]
	graph = Digraph(name = graph_name, format = 'png', engine = 'dot', directory = os.path.join(os.path.dirname(savepath), 'dotdata'))
	graph.attr('graph', dpi = '300')
	# graph.attr('node', shape = 'circle', fixedsize = 'True')
	graph.attr('node', shape = 'box')
	row_idx, column_idx = np.nonzero(net.data)
	for r, c in zip(row_idx, column_idx):
		fillcolor = color_scheme.get(atlasobj.ticks[r], default_fillcolor)
		graph.node(atlasobj.ticks[r], atlasobj.ticks[r] + '\n' + atlasobj.region_names[r], style = 'filled', fillcolor = fillcolor)
		fillcolor = color_scheme.get(atlasobj.ticks[c], default_fillcolor)
		graph.node(atlasobj.ticks[c], atlasobj.ticks[c] + '\n' + atlasobj.region_names[c], style = 'filled', fillcolor = fillcolor)
		if atlasobj.ticks[r][0] != 'A' and atlasobj.ticks[c][0] != 'A' and atlasobj.ticks[r][0] != atlasobj.ticks[c][0]:
			# L3 -> R6 etc
			graph.edge(atlasobj.ticks[r], atlasobj.ticks[c], color = 'red')
		elif atlasobj.ticks[r][0] == 'A' and atlasobj.ticks[c][0] != 'A' and atlasobj.ticks[r][1] != atlasobj.ticks[c][0]:
			# AL91 -> R6 etc
			graph.edge(atlasobj.ticks[r], atlasobj.ticks[c], color='red')
		elif atlasobj.ticks[r][0] != 'A' and atlasobj.ticks[c][0] == 'A' and atlasobj.ticks[r][0] != atlasobj.ticks[c][1]:
			# L2 -> AR96 etc
			graph.edge(atlasobj.ticks[r], atlasobj.ticks[c], color='red')
		elif atlasobj.ticks[r][0] == 'A' and atlasobj.ticks[c][0] == 'A' and atlasobj.ticks[r][1] != atlasobj.ticks[c][1]:
			# AL93 -> AR96 etc
			graph.edge(atlasobj.ticks[r], atlasobj.ticks[c], color='red')
		else:
			graph.edge(atlasobj.ticks[r], atlasobj.ticks[c])
	graph.render()
	if os.path.exists(os.path.join(os.path.dirname(savepath), graph_name + '.png')):
		os.remove(os.path.join(os.path.dirname(savepath), graph_name + '.png'))
	os.rename(os.path.join(os.path.dirname(savepath), 'dotdata', graph_name + '.gv.png'), os.path.join(os.path.dirname(savepath), graph_name + '.png'))

def plot_local_digraph(net, nodeIdx, savepath, color_scheme = {}):
	"""
	Plot local networks related to nodeIdx
	The net should be a (binary) square matrix, not necessarily symmetric however.
	All paths related to nodeIdx will be plotted
	"""
	default_fillcolor = 'white'
	os.makedirs(os.path.join(os.path.dirname(savepath), 'dotdata'), exist_ok = True)
	atlasobj = net.atlasobj
	# will save to graph_name.gv and graph_name.gv.png
	graph_name = os.path.splitext(os.path.basename(savepath))[0]
	graph = Digraph(name = graph_name, format = 'png', engine = 'dot', directory = os.path.join(os.path.dirname(savepath), 'dotdata'))
	graph.attr('graph', dpi = '300')
	# graph.attr('node', shape = 'circle', fixedsize = 'True')
	graph.attr('node', shape = 'box')
	# out connection first
	node_idx_list = [nodeIdx]
	finished_node = []
	row_idx, column_idx = np.nonzero(net.data)
	while node_idx_list:
		current_node = node_idx_list.pop()
		fillcolor = color_scheme.get(atlasobj.ticks[current_node], default_fillcolor)
		graph.node(atlasobj.ticks[current_node], atlasobj.ticks[current_node] + '\n' + atlasobj.region_names[current_node], style = 'filled', fillcolor = fillcolor)
		if current_node in finished_node:
			continue
		for r, c in zip(row_idx, column_idx):
			if r != current_node and c != current_node:
				continue
			elif r == current_node and c not in finished_node:
				node_idx_list.append(c)
			elif c == current_node and r not in finished_node:
				node_idx_list.append(r)
			else:
				continue
			if atlasobj.ticks[r][0] != atlasobj.ticks[c][0]:
				# L2 -> R6 etc
				graph.edge(atlasobj.ticks[r], atlasobj.ticks[c], color = 'red')
			else:
				graph.edge(atlasobj.ticks[r], atlasobj.ticks[c])
		finished_node.append(current_node)
	# seed node
	graph.node(atlasobj.ticks[nodeIdx], atlasobj.ticks[nodeIdx] + '\n' + atlasobj.region_names[nodeIdx], style = 'filled', fillcolor = 'turquoise')
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
