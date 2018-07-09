"""Feature data container.

Net is a network feature.
Attr is a attribute feature.
Both have corresponding atlasobj in them.
You can create sub-net or sub-attr, the atlasobj is also subbed.
"""
import csv, os
import numpy as np
from pathlib import Path
from ..util import dataop, path
from ..util.loadsave import save_csvmat, load_csvmat

class Attr:
    """Attr is attribute, it is a one dimensional vector.
    
    The dimension of the vector is atlasobj.count.
    """
    def __init__(self, data, atlasobj, name='attr'):
        """Init the attr, using data, atlasobj, and name.

        The name can be any string that can be useful.
        """
        self.data = data
        self.atlasobj = atlasobj
        self.name = name

    def copy(self):
        """Copy the attr."""
        newattr = Attr(self.data.copy(), self.atlasobj, self.name)
        return newattr

    def gensub(self, subatlasname, subindexes):
        """Generate a sub, with proper atlasobj."""
        subdata = dataop.sub_vec(self.data, subindexes)
        subatlasobj = self.atlasobj.create_sub(subatlasname, subindexes)
        return Attr(subdata, subatlasobj, self.name)

    def save(self, outfile, addticks=True):
        """Save the attr, can add ticks defined in atlasobj."""
        if addticks is False:
            save_csvmat(outfile, self.data)
        else:
            path.makedirs_file(outfile)
            with open(outfile, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(('Region', 'Value'))
                for tick, value in zip(self.atlasobj.ticks, self.data):
                    writer.writerow((tick, value))

class Net:
    """Net is network, it is a two dimensional sqaure matrix.
    
    The dimension of the vector is (atlasobj.count, atlasobj.count).
    """
    def __init__(self, data, atlasobj, name='net'):
        """Init the net, using data, atlasobj, and name.

        The name can be any string that can be useful.
        """ 
        self.data = data # np array
        self.atlasobj = atlasobj
        self.name = name
        
    def copy(self):
        """Copy the net."""
        newnet = Net(self.data.copy(), self.atlasobj, self.name)
        return newnet
    
    def gensub(self, subatlasname, subindexes):
        """Generate a sub net, with proper atlasobj."""
        subdata = dataop.sub_mat(self.data, subindexes)
        subatlasobj = self.atlasobj.create_sub(subatlasname, subindexes)
        return Net(subdata, subatlasobj, self.name)

    def save(self, outfile, addticks=True):
        """Save the net, can add ticks defined in atlasobj."""
        if addticks is False:
            save_csvmat(outfile, self.data)
        else:
            path.makedirs_file(outfile)
            with open(outfile, 'w', newline='') as f:
                writer = csv.writer(f)
                ticks = self.atlasobj.ticks
                firstrow = ['Region']
                firstrow.extend(ticks)
                writer.writerow(firstrow)
                for tick, datarow in zip(self.atlasobj.ticks, self.data):
                    currow = [tick]
                    currow.extend(datarow)
                    writer.writerow(currow)

class DynamicNet:
    """
    Dynamic net is a collection of net
    It needs only contain the atlasobj of the net
    """
    def __init__(self, atlasobj, step = 3, windowLength = 100):
        self.atlasobj = atlasobj
        self.stepSize = step
        self.windowLength = windowLength
        self.dynamic_nets = []

    def loadDynamicNets(self, loadPath):
        start = 0
        while True:
            filePath = Path(os.path.join(loadPath, 'corrcoef-%d.%d.csv' % (start, start + self.windowLength)))
            if filePath.exists():
                self.dynamic_nets.append(Net(load_csvmat(filePath), self.atlasobj))
            else:
                break
            start += self.stepSize

class Mat:
    """Mat is a general array data of any dimension, with an atlasobj and a name."""
    def __init__(self, data, atlasobj, name='mat'):
        """Init the mat."""
        self.data = data
        self.atlasobj = atlasobj
        self.name = name

