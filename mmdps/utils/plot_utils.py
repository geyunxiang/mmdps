from matplotlib import cm
from matplotlib import pyplot as plt
from scipy import stats
import numpy as np
import copy

def plot_heatmap_from_net(net, title, valuerange = (-1, 1)):
	actual_plot_index = [i[0] for i in sorted(enumerate(net.template.ticks_to_plot_indexes(net.ticks)), key = lambda x:x[1])]
	return plot_heatmap_order(net.net, net.template.ticks, actual_plot_index, title, valuerange)

def plot_heatmap_order(mat, xticks, plotindexes, title, valuerange = (-1, 1)):
	"""
	mat.shape[0] must equal len(xticks) and len(plotindexes).
	plotindexes should be a permutation of range(len(xticks))
	Here data order is adjusted.
	"""
	# TODO: optimize code here, use ndarray methods.
	mat1 = np.empty(mat.shape)
	mat2 = np.empty(mat.shape)
	plot_ticks = [None] * len(xticks)
	for i in range(len(plotindexes)):
		realpos = plotindexes[i]
		mat1[i, :] = mat[realpos, :]
		plot_ticks[i] = xticks[realpos]
	for i in range(len(plotindexes)):
		realpos = plotindexes[i]
		mat2[:, i] = mat1[:, realpos]
	return plot_heatmap(mat2, plot_ticks, title, valuerange = valuerange)

def plot_heatmap(mat, xticks, title, valuerange = (-1, 1)):
	"""
	actually plotting a mat using default orders and ticks.
	"""
	cmap = cm.coolwarm
	fig = plt.figure(figsize = (20, 20))
	axim = plt.imshow(mat, interpolation = 'none', cmap = cmap, vmin = valuerange[0], vmax = valuerange[1])
	nrow, ncol = mat.shape
	ax = fig.gca()
	ax.set_xticks(range(len(xticks)))
	ax.set_xticklabels(xticks, rotation = 90)
	ax.set_yticks(range(len(xticks)))
	ax.set_yticklabels(xticks)
	
	ax.set_xlim(-0.5, ncol-0.5)
	ax.set_ylim(nrow-0.5, -0.5)
	plt.title(title, fontsize = 30)
	fig.colorbar(axim, fraction = 0.046, pad = 0.04)
	return fig

def adjust_mat_col_order(mat, template):
	mat1 = np.empty(mat.shape)
	for i in range(template.count):
		realpos = template.plotindexes[i]
		mat1[:, i] = mat[:, realpos]
	return mat1

def sub_matrix(mat, idx):
	npidx = np.array(idx)
	return mat[npidx[:, np.newaxis], npidx]

def sub_list(l, idx):
	nl = []
	for i in idx:
		nl.append(l[i])
	return nl

def generate_edge_file(nodeFilePath, edgeFilePath, edgeDict):
	"""
	generate an edge file for BrainNet Viewer
	edgeDict = {'L2-R5':0.345}
	"""
	nodeList = []
	with open(nodeFilePath) as nodeFile:
		counter = 0
		for line in nodeFile.readlines():
			counter += 1
			line = line.strip().split('\t')
			if len(line) < 2:
				# last line
				continue
			if counter >= 83 and counter % 2 == 1:
				nodeList.append('AL%d' % (counter + 8))
			elif counter >= 83 and counter % 2 == 0:
				nodeList.append('AR%d' % (counter + 8))
			else:
				nodeList.append(line[-1])
	edgeMatrix = np.zeros((len(nodeList), len(nodeList)))
	for edge in edgeDict:
		xtick = edge.split('-')[0]
		ytick = edge.split('-')[1]
		edgeMatrix[nodeList.index(xtick), nodeList.index(ytick)] = edgeDict[edge]
		edgeMatrix[nodeList.index(ytick), nodeList.index(xtick)] = edgeDict[edge]
	save_matrix_csv_style(edgeMatrix, edgeFilePath)

def save_matrix_csv_style(mat, filePath):
	xlim = mat.shape[0]
	ylim = mat.shape[1]
	xidx = 0
	with open(filePath, 'w') as f:
		while xidx < xlim:
			yidx = 0
			while yidx < ylim:
				if yidx + 1 < ylim:
					f.write('%f\t' % mat[xidx, yidx])
				elif xidx + 1 < xlim:
					f.write('%f\n' % mat[xidx, yidx])
				else:
					f.write('%f' % mat[xidx, yidx])
				yidx += 1
			xidx += 1