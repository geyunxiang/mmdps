"""Load and save several file formats."""

import os
import json
from collections import OrderedDict
import nibabel as nib
import numpy as np

def load_txt(txtfile):
    """Load txt list file, line by line."""
    with open(txtfile, 'r') as f:
        return [l.strip() for l in f if l.strip()]

def save_txt(txtfile, lines):
    """Save line of lines to txt file."""
    with open(txtfile, 'w') as f:
        [f.write(line + '\n') for line in lines]

def load_json(jfile):
    """Load json file."""
    with open(jfile, encoding='utf-8') as f:
        return json.load(f)

def save_json(jfile, d):
    """Save dict to json file."""
    with open(jfile, encoding='utf-8') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

def load_json_ordered(jfile):
    """Load json file ordered."""
    with open(jfile, encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=OrderedDict)
    
def save_json_ordered(jfile, d):
    """Save json file ordered."""
    with open(jfile, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

def load_nii(niifile):
    """Load nifti file.

    This will load the nii file as closest canonical.
    Use this wheneven possible.
    If use nib.load, somethings the L and R are flipped.
    """
    img = nib.load(niifile)
    canonical_img = nib.as_closest_canonical(img)
    return canonical_img

def load_csvmat(matfile, delimiter = ','):
    """
    Load csv array in csv file.
    The return value is a (n,) np array for 1-D vector or a (m, n) np array for 2-D matrix
    """
    return np.loadtxt(matfile, delimiter = delimiter)

def save_csvmat(matfile, mat, delimiter = ','):
    """Save csv array in csv file."""
    os.makedirs(os.path.dirname(os.path.abspath(matfile)), exist_ok=True)
    np.savetxt(matfile, mat, delimiter=delimiter)

def load_rawtext(textfile):
    with open(textfile) as f:
        return f.read()

def save_rawtext(textfile, s):
    with open(textfile, 'w') as f:
        f.write(s)
        
