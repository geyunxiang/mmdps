"""Attr procs.

Proper scale for plot in bnv.
"""

# from . import bnv
from mmdps.vis import bnv

##AttrProcsDict = {'interBC': bnv.ScaleProc(0.004).proc,
##                 'interLE': bnv.ScaleProc(4).proc,
##                 'interWD': bnv.ScaleProc(0.03).proc}

# The procs dict
AttrProcsDict = {
    'bold_interBC': bnv.ScaleProc(0.004).proc,
    'bold_interLE': bnv.ScaleProc(4).proc,
    'bold_interWD': bnv.ScaleProc(0.03).proc,
    'dwi_FA': bnv.ScaleProc(3).proc,
    'dwi_MD': bnv.ScaleProc(1000).proc
    }


def reload(config):
    """Update procs."""
    AttrProcsDict.update(config)
    
def get(attrname):
    """Get the proc by attrname."""
    return AttrProcsDict.get(attrname, None)
    
