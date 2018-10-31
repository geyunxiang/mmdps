"""Tools for DWI data processing.

Useful tools for DWI data processing, mostly base on dipy.
"""

import os.path
import nibabel as nib
from dipy.align.reslice import reslice
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from dipy.viz import fvtk

def get_dwi_file_path(folder, niiname, gz=False):
    """Get dwi volume, bval and bvec file path."""
    fdwi = os.path.join(folder, niiname+'.nii')
    if gz:
        fdwi = fdwi + '.gz'
    fbval = os.path.join(folder, niiname+'.bval')
    fbvec = os.path.join(folder, niiname+'.bvec')
    return fdwi, fbval, fbvec

def get_dwi_img_gtab(fdwi, fbval, fbvec):
    """Get dwi image gradient table."""
    img = nib.load(fdwi)
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
    gtab = gradient_table(bvals, bvecs)
    return img, gtab

def get_fvtk_streamlines_actor(streamlines):
    """Get vtk streamline actor."""
    streamlines_actor = fvtk.line(streamlines)
    return streamlines_actor

def save_streamlines_to_trk(streamlines, affine, fileobj):
    """Save streamlines to trackvis file.
    
    Use this to generate a trk file, which can be opened in trackvis software.
    """
    tracto = nib.streamlines.Tractogram(streamlines, affine_to_rasmm=affine)
    trkfile = nib.streamlines.TrkFile(tracto)
    trkfile.save(fileobj)

def load_TrkFile(fileobj):
    """Load trk file."""
    trkfile = nib.streamlines.TrkFile.load(fileobj)
    return trkfile

def load_streamlines_from_trk(fileobj):
    """Load streamlines in trk file."""
    trkfile = load_TrkFile(fileobj)
    return trkfile.streamlines

def reslice_img(img, new_zooms):
    """Reslice image.
    
    For tractography, do iso reslice and use iso dimension dwi files.
    """
    data = img.get_data()
    affine = img.get_affine()
    zooms = img.get_header().get_zooms()[:3]
    data2, affine2 = reslice(data, affine, zooms, new_zooms)
    new_img = nib.Nifti1Image(data2.astype('int16'), affine2)
    print('reslice_img;', 'old_zooms:', zooms, 'new_zooms:', new_zooms)
    return new_img
    
