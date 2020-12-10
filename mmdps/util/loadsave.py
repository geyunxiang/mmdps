"""Load and save several file formats."""

import os
import json
import csv
from collections import OrderedDict
import nibabel as nib
import numpy as np
import scipy.io as scio

from mmdps.util import path

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
    with open(jfile, 'w', encoding='utf-8') as f:
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

def load_mat(matfile):
    """
    Load MATLAB .mat file
    return a dict
    """
    dic = scio.loadmat(matfile)
    dic.pop('__header__')
    dic.pop('__version__')
    dic.pop('__globals__')
    return dic

def load_csvmat(matfile, delimiter = ','):
    """
    Load csv array in csv file.
    The return value is a (n,) np array for 1-D vector or a (m, n) np array for 2-D matrix
    """
    try:
        ret = np.loadtxt(matfile, delimiter = delimiter)
    except ValueError:
        # work around for csv files with comma at the end
        ret = np.genfromtxt(matfile, delimiter=',', dtype=np.float64)
        if len(ret.shape) > 1:
            # does not support loading network
            raise Exception
        ret = ret[:-1]
    return ret

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

def save_list_to_csv(list_data, outfile):
    """
    save a list of dicts to a csv file
    :param list_data: a list of dicts
    :param outfile:
    :return:
    """
    path.makedirs_file(outfile)
    with open(outfile, 'w', newline = '') as f:
        writer = csv.DictWriter(f, list_data[0].keys(), delimiter = ',')
        writer.writeheader()
        for itm in list_data:
            writer.writerow(itm)

def load_csv_to_list(outfile):
    """
    load csv file as a list of dicts
    """
    ret = []
    with open(outfile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ret.append(row)
    return ret

def load_csv_to_dict(outfile, key_column):
    """
    Load csv file as a dict. Specify which column value should be used as key
    """
    ret = dict()
    with open(outfile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ret[row[key_column]] = row
    return ret
