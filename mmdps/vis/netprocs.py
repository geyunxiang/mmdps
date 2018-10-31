"""Default net procs.
"""

# net default valuerange mapping
NetValueRangeDict = {
    'bold_net': (-1, 1),
    'dwi_net': (0, 10)
    }

def get_valuerange(netname):
    """Get the default valuerange by netname."""
    return NetValueRangeDict.get(netname, (-1, 1))
