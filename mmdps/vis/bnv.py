"""bnv is used to plot brainnet viewer images.

Check the BrainNetViewer manual for details.
Plot is slow, consider add p.plot_net and similar to a list and use parabase
to run the plots in parallel.
"""


import os
import csv
import numpy as np
# from ..util import path
# from .. import rootconfig
# from ..proc import job
# from ..proc import netattr
from mmdps.util import path
from mmdps import rootconfig
from mmdps.proc import job, netattr

# built in mesh
BuiltinMeshDict = {'ch2cere': 'ch2cere.nv', 'icbm152smoothed': 'icbm152smoothed.nv'}
# built in config
BuiltinConfigDict = {'nodeonly': 'nodeonly.mat', 'edgeonly': 'edgeonly.mat', 'nodeedge': 'nodeedge.mat'}

def sub_list(l, idx):
    """Sub list by index."""
    nl = []
    for i in idx:
        nl.append(l[i])
    return nl

def fullfile_bnvdata(*p):
    """full file for bnv data."""
    return os.path.join(rootconfig.path.bnvdata, *p)

def get_mesh(meshname=None):
    """Get mesh path by name."""
    if meshname is None:
        meshname = 'icbm152smoothed'
    file = BuiltinMeshDict.get(meshname, 'icbm152smoothed')
    return fullfile_bnvdata(file)

def get_cfg(cfgname=None):
    """Get config path by name."""
    if cfgname is None:
        cfgname = 'nodeonly'
    file = BuiltinConfigDict.get(cfgname, 'nodeonly')
    return fullfile_bnvdata(file)
    
def gen_matlab(nodepath, edgepath, title, outpath, bnv_mesh, bnv_cfg):
    """Generate matlab string for plotting bnv image."""
    rows = []
    rows.append("nodefile = '{}';".format(nodepath))
    rows.append("edgefile = '{}';".format(edgepath))
    rows.append("desc = '{}';".format(title))
    rows.append("outpath = '{}';".format(outpath))
    rows.append("bnv_mesh = '{}';".format(bnv_mesh))
    rows.append("bnv_cfg = '{}';".format(bnv_cfg))
    rows.append('draw_brain_net(nodefile, edgefile, desc, outpath, bnv_mesh, bnv_cfg);')
    mstr = ''.join(rows)
    return mstr

class MatProc:
    """Matrix proc."""
    def proc(self, data):
        """Input data, return proced data."""
        return data
    
class ScaleProc:
    """Scale proc."""
    def __init__(self, scale):
        """Init use scale."""
        self.scale = scale
        
    def proc(self, data):
        """Scale the data."""
        newdata = data * self.scale
        return newdata

class ThresholdProc:
    """Threshold proc."""
    def __init__(self, thres):
        """Init use the threshold."""
        self.thres = thres

    def proc(self, data):
        """Threshold the data."""
        newdata = data.copy()
        newdata[data <= self.thres] = 0
        return newdata

class AbsThresholdProc:
    """Absolute threshold proc."""
    def __init__(self, thres):
        """Init use threshold."""
        self.thres = thres

    def proc(self, data):
        """Threshold data after abs."""
        newdata = data.copy()
        newdata[np.abs(data)<self.thres] = 0
        return newdata
    
class BNVNode:
    """BNV node file manipulation.
    
    nodefile is the corresponding node data file in bnv.
    """
    def __init__(self, nodefile=None):
        """Init use nodefile."""
        nodedata = []
        if nodefile:
            with open(nodefile, newline='') as f:
                csvcontent = csv.reader(f, delimiter='\t')
                for row in csvcontent:
                    nodedata.append(row)
        self.origin_nodedata = nodedata
        self.nodedata = nodedata.copy()
        self.count = len(nodedata)
    
    def reset(self):
        """Reset the data to original."""
        self.nodedata = self.origin_nodedata.copy()

    def write(self, outnodefile):
        """Write current data to a new node file."""
        path.makedirs_file(outnodefile)
        with open(outnodefile, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.nodedata)
        
    def change_column(self, col, colvalue):
        """Change one column in the node file."""
        for irow in range(self.count):
            self.nodedata[irow][col] = colvalue[irow]
        
    def change_modular(self, modular):
        """Change the modular column."""
        self.change_column(3, modular)

    def change_value(self, value):
        """Change the value column."""
        self.change_column(4, value)

    def change_label(self, label):
        """Change the label column."""
        self.change_column(5, label)
    
    def copy(self):
        """Copy the bnvnode object."""
        bnvnode = BNVNode()
        bnvnode.nodedata = self.nodedata.copy()
        bnvnode.count = self.count
        return bnvnode

    def copy_sub(self, subindexes):
        """Create a sub bnvnode object use indexes in subindexes and return it."""
        subbnvnode = BNVNode()
        subbnvnode.nodedata = sub_list(self.nodedata.copy(), subindexes)
        subbnvnode.count = len(subindexes)
        return subbnvnode

class BNVEdge:
    """BNV edge file manipulation.
    
    edgefile is the corresponding edge data file in bnv.
    It is just a square matrix represents the network.
    """
    def __init__(self, net):
        """Init use Net."""
        self.net = net

    def write(self, outedgefile):
        """Write the edge file."""
        path.makedirs_file(outedgefile)
        np.savetxt(outedgefile, self.net.data, delimiter=' ')
        
class BNVPlot:
    """BNV plot is used to init one bnv plot, and run the plot."""
    def __init__(self, net, attr, title, outfilepath, f_netproc=None, f_attrproc=None):
        """Init the plot.

        net, the edge file. Can be None.
        attr, the value column in node file. Can be None.
        title, the image title.
        outfilepath, output image file path.
        f_netproc, proc applied to net before plot.
        f_attrproc, proc applied to attr before plot.
        """
        self.net = net
        if attr is None:
            attr = self.onesattr(net)
        self.attr = attr
        if f_netproc:
            self.net.data = f_netproc(net.data)
        if f_attrproc:
            self.attr.data = f_attrproc(attr.data)
        self.title = title
        self.outfilepath = outfilepath
        self.atlasobj = self.attr.atlasobj
        self.count = self.atlasobj.count
        self.outfilename = os.path.basename(outfilepath)
        self.bnvdatapath = os.path.dirname(outfilepath)

    def onesattr(self, net):
        """Create a attr of all ones."""
        return netattr.Attr(np.ones(net.atlasobj.count), net.atlasobj)
    
    def fullpath(self, *p):
        """Full path for bnv data."""
        return os.path.join(self.bnvdatapath, 'bnvdata', *p)
    
    def gen_node(self):
        """Generate node file."""
        bnvnode = self.attr.atlasobj.bnvnode
        modulars = np.ones(self.count)
        values = self.attr.data
        bnvnode.change_modular(modulars)
        bnvnode.change_value(values)
        nodepath = self.fullpath(self.outfilename + '.node')
        bnvnode.write(nodepath)
        return nodepath

    def gen_edge(self):
        """Generate edge file."""
        bnvedge = BNVEdge(self.net)
        edgepath = self.fullpath(self.outfilename + '.edge')
        bnvedge.write(edgepath)
        return edgepath
    
    def plot(self, plottype):
        """Plot.
        
        TODO:
        Plot by type.
        """
        pass

    def get_mesh(self, meshname=None):
        """Get the mesh path.

        Override this to provide your own mesh file.
        """
        return get_mesh(meshname)

    def get_cfg(self, cfgname=None):
        """Get the config path.

        Override this to provide your own config file.
        """
        return get_cfg(cfgname)
    
    def plot_attr(self):
        """Plot attribute only."""
        nodepath = self.gen_node()
        bnv_mesh = self.get_mesh()
        bnv_cfg = self.get_cfg('nodeonly')
        mstr = gen_matlab(nodepath, '', self.title, self.outfilepath, bnv_mesh, bnv_cfg)
        j = job.MatlabJob('bnv', mstr)
        j.run()

    def plot_net(self):
        """Plot net only."""
        nodepath = self.gen_node()
        edgepath = self.gen_edge()
        bnv_mesh = self.get_mesh()
        bnv_cfg = self.get_cfg('edgeonly')
        mstr = gen_matlab(nodepath, edgepath, self.title, self.outfilepath, bnv_mesh, bnv_cfg)
        j = job.MatlabJob('bnv', mstr)
        j.run()
        
    def plot_netattr(self):
        """Plot net and attr."""
        nodepath = self.gen_node()
        edgepath = self.gen_edge()
        bnv_mesh = self.get_mesh()
        bnv_cfg = self.get_cfg('nodeedge')
        mstr = gen_matlab(nodepath, edgepath, self.title, self.outfilepath, bnv_mesh, bnv_cfg)
        j = job.MatlabJob('bnv', mstr)
        j.run()
        
    
