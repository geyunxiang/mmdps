"""File operations.

"""

import os
import subprocess
import gzip
import shutil
# from .. import rootconfig
# from . import toolman, run, path
from mmdps import rootconfig
from mmdps.util import toolman, run, path

def getfirstpart(s):
    """first part before _."""
    i = s.find('_')
    return s[0:i]

def edit_text(filepath):
    """Edit text use text editor."""
    editorpath = rootconfig.path.texteditor
    run.popen([editorpath, filepath])
    
def edit_json(filepath, filename, firstpart):
    """Edit json use dedicated tool if possible, otherwise use text editor."""
    manager = toolman.get_default_manager()
    tool = manager.find(firstpart)
    print(firstpart)
    if tool is None:
        print('No proper ui, use text editor instead')
        edit_text(filepath)
    else:
        tool.opentool(filepath)
        
def edit(filepath):
    """Edit the file use proper program."""
    if not os.path.isfile(filepath):
        print('{} not found'.format(filepath))
    else:
        filename = os.path.basename(filepath)
        firstpart = getfirstpart(filename)
        filenoext, ext = os.path.splitext(filename)
        if ext == '.json':
            edit_json(filepath, filename, firstpart)
        elif ext == '.txt':
            edit_text(filepath)
            
            
def open_nii(niifile):
    """Open nifti file use nii viewer."""
    if os.path.isfile(niifile):
        cmdexe = rootconfig.path.niiviewer
        subprocess.Popen([cmdexe, niifile])
    else:
        print('File not found')

def gz_zip(infile, outfile=None):
    """Gz zip file."""
    if outfile is None:
        outfile = infile + '.gz'
    try:
        with open(infile, 'rb') as fin,\
             gzip.open(outfile, 'wb') as fout:
            shutil.copyfileobj(fin, fout)
    except FileNotFoundError:
        print('File not found', infile, 'or', outfile)
        return None
    return outfile

def gz_unzip(gzfile, outfile=None):
    """Gz un zip file."""
    if outfile == None:
        outfile = gzfile[0:-3]
    try:
        with gzip.open(gzfile, 'rb') as fin,\
             open(outfile, 'wb') as fout:
            shutil.copyfileobj(fin, fout)
    except FileNotFoundError:
        print('File not found', gzfile, 'or', outfile)
        return None
    return outfile


