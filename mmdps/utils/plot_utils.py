from matplotlib import pyplot as plt
from scipy import stats
import numpy as np
import copy

def adjust_mat_col_order(mat, template):
	mat1 = np.empty(mat.shape)
	for i in range(template.count):
		realpos = template.plotindexes[i]
		mat1[:, i] = mat[:, realpos]
	return mat1

def plot_heatmap_template(sqmat, template, cmap, valuerange=(-1,1)):
	mat1 = np.empty(sqmat.shape)
	mat2 = np.empty(sqmat.shape)
	for i in range(template.count):
		realpos = template.plotindexes[i]
		mat1[i, :] = sqmat[realpos, :]
	for i in range(template.count):
		realpos = template.plotindexes[i]
		mat2[:, i] = mat1[:, realpos]
	ticks = [None] * template.count
	for i in range(template.count):
		realpos = template.plotindexes[i]
		ticks[i] = template.ticks[realpos]
	return plot_heatmap(mat2, cmap, ticks, valuerange=valuerange)

def sub_matrix(mat, idx):
	npidx = np.array(idx)
	return mat[npidx[:, np.newaxis], npidx]

def sub_list(l, idx):
	nl = []
	for i in idx:
		nl.append(l[i])
	return nl

def plot_heatmap_template_subnet(sqmat, template, cmap, rawindexes, valuerange=(-1,1)):
	sqmat = sub_matrix(sqmat, rawindexes)
	subtemplate = dummy()
	subtemplate.count = len(rawindexes)
	subtemplate.ticks = sub_list(template.ticks, rawindexes)
	rawplotindexes = sub_list(template.plotindexes, rawindexes)
	plotindexesrank = np.array(rawplotindexes).argsort().argsort()
	subtemplate.plotindexes = plotindexesrank
	return plot_heatmap_template(sqmat, subtemplate, cmap, valuerange)

def plot_heatmap(mat, cmap, xticks, valuerange=(-1,1)):
	fig = plt.figure(figsize=(20,20))
	axim = plt.imshow(mat, interpolation='none', cmap=cmap,
					  vmin=valuerange[0], vmax=valuerange[1])
	nrow, ncol = mat.shape
	half = ncol/2
#    plt.plot([half-0.5, half-0.5], [-0.5, nrow-0.5], color='k')
	half = nrow/2
#    plt.plot([-0.5, ncol-0.5], [half-0.5, half-0.5], color='k')
	
	ax = fig.gca()
	ax.set_xticks(range(len(xticks)))
	ax.set_xticklabels(xticks, rotation=90)
	ax.set_yticks(range(len(xticks)))
	ax.set_yticklabels(xticks)
	
	ax.set_xlim(-0.5, ncol-0.5)
	ax.set_ylim(nrow-0.5, -0.5)

	fig.colorbar(axim, fraction=0.046, pad=0.04)
	return fig
