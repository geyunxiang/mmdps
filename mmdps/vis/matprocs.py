"""Mat procs.

"""
import numpy as np

def noproc(mat):
    """no proc."""
    return mat

def absolute(mat):
    """Absolute only."""
    return np.abs(mat)

def positiveonly(mat):
    """Positive only."""
    retmat = mat.copy()
    retmat[retmat < 0] = 0
    return retmat

def negativeonly(mat):
    """Negative only."""
    retmat = mat.copy()
    retmat[retmat > 0] = 0
    return retmat
