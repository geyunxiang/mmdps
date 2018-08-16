"""Loader is used to load all fusion input.

The fusion input is loaded by loaders.
The loaders are created by fusion constructor. There are config files
to config every loader.
"""
import os
import csv
import numpy as np
# from . import netattr
# from ..util.loadsave import load_csvmat, load_txt
# from ..util import path
import netattr
from mmdps.util.loadsave import load_csvmat, load_txt
from mmdps.util import path

class Loader:
    """Base class Loader is used to load raw array data."""
    def __init__(self, mainfolder, atlasobj, foldername, csvdict):
        """Init the loader."""
        self.mainfolder = mainfolder
        self.atlasobj = atlasobj
        self.foldername = foldername
        self.csvdict = csvdict
        self.f_preproc = None
        
    def names(self):
        """The feature names in csvdict."""
        thenames = []
        for name in self.csvdict:
            thenames.append(name)
        return thenames
    
    def fullfile(self, mriscan, *p):
        """Full path for one feature."""
        return os.path.join(self.mainfolder, mriscan, self.atlasobj.name, *p)

    def csvfilename(self, netattrname):
        """Get the csv filename by feature name."""
        return self.csvdict.get(netattrname, '')

    def loadfilepath(self, mriscan, netattrname):
        """File path for one feature."""
        return self.fullfile(mriscan, self.foldername, self.csvfilename(netattrname))
    
    def loaddata(self, mriscan, netattrname):
        """Load the feature specified by mriscan and feature name.

        Use set_preproc to set a pre-processing function.
        """
        csvfile = self.loadfilepath(mriscan, netattrname)
        resmat = load_csvmat(csvfile)
        if type(self.f_preproc) is dict:
            if mriscan in self.f_preproc:
                f = self.f_preproc[mriscan]
                if f:
                    resmat = f(resmat)
        elif self.f_preproc:
            resmat = self.f_preproc(resmat)
        return resmat
    
    def load(self, mriscan, netattrname):
        """Load Mat, with atlasobj."""
        data = self.loaddata(mriscan, netattrname)
        netattrobj = netattr.Mat(data, self.atlasobj, mriscan)
        return netattrobj

    def getshape(self, mriscan, netattrname):
        """Get data shape."""
        return self.loaddata(mriscan, netattrname).shape

    def set_preproc(self, f_preproc):
        """Set the pre-process function. A function or mriscan:function dict.
        Will be used when loaddata is called.

        If f_preproc is a function, it will be used like m=f_preproc(m).
        If f_preproc is a dict, it will be used like m=f_preproc[mriscan](m).
        """
        self.f_preproc = f_preproc
        
    def loadvstack(self, mriscans, netattrname):
        """Load all data in every mriscan in mriscans.

        Every feature data for one mriscan is flattened, before vstacked to a matrix.
        """
        datalist = []
        for mriscan in mriscans:
            curdata = self.loaddata(mriscan, netattrname)
            datalist.append(curdata.flatten())
        datavstack = np.vstack(datalist)
        return datavstack
    
class AttrLoader(Loader):
    """Attribute loader."""
    def load(self, mriscan, attrname):
        """Load the attribute object, with atlasobj."""
        attrdata = self.loaddata(mriscan, attrname)
        attr = netattr.Attr(attrdata, self.atlasobj, mriscan)
        return attr

    def loadvstackmulti(self, mriscans, attrnames):
        """Load all data in every mriscans in mriscans, and every attr in attrnames.
        
        mriscan0 | attr0v attr1v attr2v
        mriscan1 | attr0v attr1v attr2v
        """
        attrvs = []
        for attrname in attrnames:
            attrv = self.loadvstack(mriscans, attrname)
            attrvs.append(attrv)
        return np.hstack(attrvs)
        
class NetLoader(Loader):
    """Net loader."""
    def load(self, mriscan, attrname):
        """Load the net object, with atlasobj."""
        netdata = self.loaddata(mriscan, attrname)
        net = netattr.Net(netdata, self.atlasobj, mriscan)
        return net

class ScoreLoader:
    """Score loader is used to load clinical score data."""
    def __init__(self, scoreconfigdict):
        """Init the loader. 
        
        After init, there are mriscans, scorenames,
        scores_dict[scorename], mriscan_scores_dict[mriscan].
        """
        self.scorecsvfile = scoreconfigdict['csvfile']
        self.load_scorecsvfile()
        
    def load_scorecsvfile(self):
        """Load the score csv file."""
        if not os.path.isfile(self.scorecsvfile):
            return
        with open(self.scorecsvfile, newline='') as f:
            self.mriscan_scores_dict = {}
            self.mriscans = []
            reader = csv.reader(f)
            headers = next(reader)
            self.scorenames = headers[1:]
            self.scores_dict = {}
            for scorename in self.scorenames:
                self.scores_dict[scorename] = []
            for row in reader:
                mriscan = row[0]
                self.mriscans.append(mriscan)
                curscores = [float(s) for s in row[1:]]
                self.mriscan_scores_dict[mriscan] = curscores
                for iscore, score in enumerate(curscores):
                    self.scores_dict[self.scorenames[iscore]].append(curscores[iscore])

    def loadvstack(self, mriscans):
        """Load all scores vstacked to a matrix for all mriscans, in order."""
        scoreslist = []
        for mriscan in mriscans:
            curscores = self.mriscan_scores_dict[mriscan]
            scoreslist.append(curscores)
        scoresvstack = np.vstack(scoreslist)
        return scoresvstack
    
class GroupLoader:
    """Group loader is used to load a group."""
    def __init__(self, groupconfigdict):
        """Init the loader using config dict."""
        self.mriscanstxt = groupconfigdict['txtfile']
        self.load_mriscanstxt()

    def load_mriscanstxt(self):
        """Load the mriscans txt file."""
        if not os.path.isfile(self.mriscanstxt):
            return
        self.mriscans = load_txt(self.mriscanstxt)
        self.people = self.build_internals(self.mriscans)

    def build_internals(self, mriscans):
        """Build internals."""
        peopleset = set()
        person_mriscans_dict = {}
        for mriscan in mriscans:
            person, mriscandate = path.name_date(mriscan)
            peopleset.add(person)
            if person in person_mriscans_dict:
                person_mriscans_dict[person].append(mriscan)
            else:
                person_mriscans_dict[person] = [mriscan]
        self.person_mriscans_dict = person_mriscans_dict
        return sorted(list(peopleset))
    
    def person_to_mriscans(self, person):
        """Person to mriscans, in this group."""
        return self.person_mriscans_dict.get(person, [])