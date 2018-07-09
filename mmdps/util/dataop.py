"""Data operation.
"""

import numpy as np



def sub_mat(mat, indexes):
    """Sub matrix."""
    npindexes = np.array(indexes)
    return mat[npindexes[:, np.newaxis], npindexes]

def sub_vec(vec, indexes):
    """Sub vector."""
    npindexes = np.array(indexes)
    return vec[npindexes]

def sub_list(l, indexes):
    """Sub list."""
    return [l[i] for i in indexes]

def complement_indexes(indexes, count):
    """Complement indexes, up to count."""
    r = []
    set_indexes = set(indexes)
    for i in range(count):
        if i not in set_indexes:
            r.append(i)
    return r

def mat_fill_rows(mat, indexes, value):
    """Fill matrix indexes rows with value."""
    npindexes = np.array(indexes)
    newmat = mat.copy()
    newmat[indexes, :] = value
    return newmat

def sub_mat_rows(mat, indexes):
    """Sub matrix indexes rows."""
    npindexes = np.array(indexes)
    return mat[npindexes, :]


def vec_flip_lr(vec, atlasobj):
    """Flip left right of vector based on atlasobj."""
    return sub_vec(vec, atlasobj.indexes_fliplr)

def mat_flip_lr(mat, atlasobj):
    """Flip left right of matrix based on atlasobj."""
    return sub_mat(mat, atlasobj.indexes_fliplr)


