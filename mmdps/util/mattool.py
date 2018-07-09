"""Matrix tools.

"""
import numpy as np
from scipy import stats



def pearsonr(xmat, yvec):
    """Calculate pearsonr.
    
    Each column in xmat acts as xvec, calculate pearsonr with yvec.
    Return the r values and p values.
    """
    nrow, ncol = xmat.shape
    assert nrow == yvec.shape[0]
    rs = np.zeros(ncol)
    ps = np.zeros(ncol)
    for i in range(ncol):
        x = xmat[:, i]
        y = yvec
        r, p = stats.pearsonr(x, y)
        rs[i], ps[i] = r, p
    return rs, ps
