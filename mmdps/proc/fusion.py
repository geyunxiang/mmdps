"""The fusion provides all needed for data fusion.

The fusion should be used to access all features.
One atlas at a time. Use the fusion object to access the atlas,
features, clinical scores and groups.
"""

import os
import csv
import glob

from collections import OrderedDict
# from . import loader
# from ..util.loadsave import load_json_ordered
import loader
from mmdps.util.loadsave import load_json_ordered

def merge_dicts(*dicts):
    """Merge several dicts to one."""
    res = OrderedDict()
    for d in dicts:
        res.update(d)
    return res

class Fusion:
    """The Fusion object provides all data for fusion.

    Use this to access everything, including features, atlasobj, scores and groups.
    After init, this fusion object will have nets, attrs, scores, groups.
    """
    def __init__(self, atlasobj, mainconfig, netattrconfig, scoresconfig, groupsconfig):
        """Init the fusion.
        
        atlasobj is the atlas object used for this fusion.
        mainconfig is the main config for this fusion, feature input folders.
        netattrconfig is the config for all the features.
        scoresconfig is the config for all the clinical scores.
        groupsconfig is the config for all the groups.
        """
        self.atlasobj = atlasobj
        self.mainconfig = mainconfig
        self.netattrconfig = netattrconfig
        self.scoresconfig = scoresconfig
        self.groupsconfig = groupsconfig
        self.init_all()

    def init_all(self):
        """Init all loaders."""
        self.mainfolder = self.mainconfig['mainfolder']
        self.init_netattr()
        self.init_groups()
        self.init_scores()
        
    def init_netattr(self):
        """Init feature loaders, net and attribute."""
        netsconfig = self.netattrconfig.get('nets', {})
        csvdict = {}
        for netname, netconfig in netsconfig.items():
            csvfile = netconfig.get('file', netname + '.csv')
            csvdict[netname] = csvfile
        self.nets = loader.NetLoader(self.mainfolder, self.atlasobj, '', csvdict)
        attrsconfig = self.netattrconfig.get('attrs', {})
        csvdict = {}
        for attrname, attrconfig in attrsconfig.items():
            csvfile = netconfig.get('file', attrname + '.csv')
            csvdict[attrname] = csvfile
        self.attrs = loader.AttrLoader(self.mainfolder, self.atlasobj, '', csvdict)

    def init_groups(self):
        """Init group loaders."""
        self.groups = OrderedDict()
        if self.groupsconfig is None:
            return
        for groupname, groupconfigdict in self.groupsconfig.items():
            curgroup = loader.GroupLoader(groupconfigdict)
            self.groups[groupname] = curgroup

    def init_scores(self):
        """Init clinical scores."""
        self.scores = OrderedDict()
        if self.scoresconfig is None:
            return
        for scorename, scoreconfigdict in self.scoresconfig.items():
            self.scores[scorename] = loader.ScoreLoader(scoreconfigdict)
        
def load_json_nonraise(jfile):
    """Load json with out exception. Return None if failed to load."""
    if os.path.isfile(jfile):
        return load_json_ordered(jfile)
    return None

def create_by_files(atlasobj, mainconffile, netattrfile, scorefile, groupfile):
    """Create the fusion by config files."""
    return Fusion(atlasobj, load_json_nonraise(mainconffile), load_json_nonraise(netattrfile),
                  load_json_nonraise(scorefile), load_json_nonraise(groupfile))

def create_by_folder(atlasobj, configsfolder):
    """Create the fusion by config folder, in which the config files reside."""
    ff = os.path.join(configsfolder, 'fusion_mainconf.json')
    nf = os.path.join(configsfolder, 'fusion_netattr.json')
    sf = os.path.join(configsfolder, 'fusion_score.json')
    gf = os.path.join(configsfolder, 'fusion_group.json')
    return create_by_files(atlasobj, ff, nf, sf, gf)
    
class ForeachBase:
    """For each iterate."""
    def __init__(self, fu, caselist):
        """Init use fusion object and all cases list."""
        self.fu = fu
        self.caselist = caselist
        self.atlasname = self.fu.atlasobj.name

    def work(self, case):
        """Test work, override to provide actual functionality."""
        print(case)
        
    def run(self):
        """Run the for each iteration. Return whateven work returns in a list."""
        rets = []
        for case in self.caselist:
            ret = self.work(case)
            rets.append(ret)
        return rets

class ForeachMRIScan(ForeachBase):
    """Iterate mriscans."""
    def __init__(self, fu, mriscans):
        """Init with mriscans."""
        super().__init__(fu, mriscans)
        self.mriscans = mriscans

class ForeachPerson(ForeachBase):
    """Iterate people."""
    def __init__(self, fu, people):
        """Init with people."""
        super().__init__(fu, people)
        self.people = people
        
