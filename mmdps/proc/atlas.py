"""Brain atlas tools.

Access brain atlases.
"""

import os
import numpy as np
# from .. import rootconfig
# from ..util import loadsave
# from ..vis import bnv
# from ..util import dataop
from mmdps import rootconfig
from mmdps.util import loadsave, dataop
from mmdps.vis import bnv

class Atlas:
    """The brain atlas.

    Init use a description desc, check atlas folder for example.
    Can be used without actual atlas nii. If do have nii, it is in atlasfolder.
    """
    def __init__(self, descdict, atlasfolder=None):
        """Init the atlas object."""
        # the original description dict
        self.dd = descdict
        # the name of the atlas
        self.name = self.dd['name']
        # if atlasfolder not specified, use default
        if atlasfolder is None:
            self.atlasfolder = os.path.join(rootconfig.path.atlas, self.name)
        else:
            self.atlasfolder = atlasfolder
        # brief description
        self.brief = self.dd['brief']
        # total region count
        self.count = self.dd['count']
        # the regions list, they are the numbers appearred in nii file, sequentially, except 0.
        self.regions = self.dd['regions']
        # the ticks list, correspond to regions
        self.ticks = self.dd['ticks']
        # the plotindexes list, n means it is the nth to be ploted.
        self.plotindexes = self.dd['plotindexes']
        # nodefile for use with brainnet viewer.
        if 'nodefile' in self.dd:
            self.nodefile = self.fullpath(self.dd['nodefile'])
            self.bnvnode = bnv.BNVNode(self.nodefile)
        # ticks_adjusted is the ticks list, adjusted using plotindexes.
        self.ticks_adjusted = self.adjust_ticks()
        # leftrightindexes in the indexes split into left and right.
        self.leftrightindexes = self.dd.get('leftrightindexes', None)
        if self.leftrightindexes:
            # indexes_fliplr is indexes with corresponding Ln and Rn flipped.
            self.indexes_fliplr = self.build_indexes_fliplr()
        # volumes to access the actual nii file.
        if 'volumes' in self.dd:
            self.add_volumes(self.dd['volumes'])
        # circos parts config folder
        self.circosfolder = self.fullpath()
        self.brainparts = None
        
    def fullpath(self, *p):
        """fullpath for atlas folder."""
        return os.path.join(self.atlasfolder, *p)

    def set_brainparts(self, name):
        from ..vis import braincircos
        circosfile = 'circosparts_{}.json'.format(name)
        self.brainparts = braincircos.BrainParts(loadsave.load_json(os.path.join(self.circosfolder, circosfile)))
    
    def get_brainparts(self):
        if self.brainparts:
            return self.brainparts
        self.set_brainparts('default')
        return self.brainparts
    
    def add_volumes(self, volumes):
        """Add volumes for actual nii files."""
        self.volumes = {}
        for volumename in volumes:
            volumes[volumename]['niifile'] = self.fullpath(volumes[volumename]['niifile'])
            self.volumes[volumename] = volumes[volumename]

    def get_volume(self, volumename):
        """Get one volume using volumename."""
        return self.volumes[volumename]
    
    def adjust_ticks(self):
        """Adjust ticks according to plotindexes."""
        adjticks = [None] * self.count
        for i in range(self.count):
            realpos = self.plotindexes[i]
            adjticks[i] = self.ticks[realpos]
        return adjticks

    def adjust_vec(self, vec):
        """Adjust a vector according to plotindexes."""
        vec_adjusted = np.zeros(vec.shape)
        for i in range(self.count):
            realpos = self.plotindexes[i]
            vec_adjusted[i] = vec[realpos]
        return vec_adjusted

    def adjust_mat(self, sqmat):
        """Adjust a matrix according to plotindexes.

        Both columns and rows are adjusted.
        """
        mat1 = np.empty(sqmat.shape)
        mat2 = np.empty(sqmat.shape)
        for i in range(self.count):
            realpos = self.plotindexes[i]
            mat1[i, :] = sqmat[realpos, :]
        for i in range(self.count):
            realpos = self.plotindexes[i]
            mat2[:, i] = mat1[:, realpos]
        return mat2

    def adjust_mat_col(self, mat):
        """Adjust matrix columns according to plotindexes.

        Only columns are adjusted, rows not adjusted.
        """
        mat1 = np.empty(mat.shape)
        for i in range(self.count):
            realpos = self.plotindexes[i]
            mat1[:, i] = mat[:, realpos]
        return mat1

    def adjust_mat_row(self, mat):
        """Adjust matrix rows according to plotindexes.
        
        Only rows are adjusted, columns not adjusted.
        """
        mat1 = np.empty(mat.shape)
        for i in range(self.count):
            realpos = self.plotindexes[i]
            mat1[i, :] = mat[realpos, :]
        return mat1
    
    def ticks_to_regions(self, ticks):
        """Convert ticks to regions."""
        if not hasattr(self, '_tickregiondict'):
            self._tickregiondict = dict([(k, v) for k, v in zip(self.ticks, self.regions)])
        regions = [self._tickregiondict[tick] for tick in ticks]
        return regions

    def regions_to_indexes(self, regions):
        """Convert regions to indexes."""
        if not hasattr(self, '_regionindexdict'):
            self._regionindexdict = dict([(k, i) for i, k in enumerate(self.regions)])
        indexes = [self._regionindexdict[region] for region in regions]
        return indexes

    def ticks_to_indexes(self, ticks):
        """Convert ticks to indexes."""
        if not hasattr(self, '_tickindexdict'):
            self._tickindexdict = dict([(k, i) for i, k in enumerate(self.ticks)])
        indexes = [self._tickindexdict[tick] for tick in ticks]
        return indexes

    def indexes_to_ticks(self, indexes):
        """Convert indexes to ticks."""
        return [self.ticks[index] for index in indexes]

    def build_indexes_fliplr(self):
        lrindex = self.leftrightindexes
        n = self.count
        lindex = lrindex[:n//2]
        rindex = lrindex[n//2:]
        indexes = list(range(n))
        for li, ri in zip(lindex, rindex):
            indexes[li] = ri
            indexes[ri] = li
        return indexes
    

    def create_sub(self, subatlasname, subindexes):
        """Create a sub atlas using specified sub indexes.
        
        Create a sub atlas with name and sub indexes. The new sub atlas can be used
        just like a normal atlas.
        """
        subdd = {}
        subdd['name'] = subatlasname
        subdd['brief'] = '{}, subnet based on {}'.format(subatlasname, self.name)
        subdd['count'] = len(subindexes)
        subdd['regions'] = dataop.sub_list(self.regions, subindexes)
        subdd['ticks'] = dataop.sub_list(self.ticks, subindexes)
        rawsubplotindexes = dataop.sub_list(self.plotindexes, subindexes)
        subdd['plotindexes'] = np.argsort(rawsubplotindexes)
        subatlasobj = Atlas(subdd)
        subatlasobj.bnvnode = self.bnvnode.copy_sub(subindexes)
        return subatlasobj

def get(atlasname):
    """Get an atlasobj with name.
    
    This is typically what you want when to get a atlas object.
    """
    jfilename = atlasname + '.json'
    jfilepath = os.path.join(rootconfig.path.atlas, jfilename)
    atlasconf = loadsave.load_json(jfilepath)
    return Atlas(atlasconf)

def getbywd():
    """Get an atlasobj by working directory.

    If current working directory is xx/xx/aal, then it will return an aal atlasobj.
    Use this when writing processing scripts. It will work regardless of the actual
    atlas.
    """
    atlasname = os.path.basename(os.getcwd())
    return get(atlasname)

def getbyenv(atlasname_default='aal'):
    """Get an atlasobj by environment variable MMDPS_CUR_ATLAS.

    If there is a environment variable MMDPS_CUR_ATLAS. Return the atlasobj specified
    by atlas name. Otherwise return the atlasobj of atlasname_default.
    Use this when writing processing scripts that should run in every atlases. 
    """
    atlasname = os.environ.get('MMDPS_CUR_ATLAS')
    if atlasname == None:
        print('MMDPS_CUR_ATLAS not set, use default', atlasname_default)
        atlasname = atlasname_default
    return get(atlasname)
