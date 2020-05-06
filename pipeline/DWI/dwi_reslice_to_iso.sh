#!/bin/bash

# Reslice DWI data to isometric
# Input: pre-processed DWI data
# Output: nodif_brain and DWI in isometric


# reslice nodif_brain to isometric
# flirt [options] -in <inputvol> -ref <refvol> -out <outputvol>
# -applyisoxfm <scale>               (as applyxfm but forces isotropic resampling)
# -applyxfm                          (applies transform (no optimisation) - requires -init)
flirt -in nodif_brain -ref nodif_brain -out iso2.0_nodif_brain -applyisoxfm 2

# generate mask
# -bin   : use (current image>0) to binarise
fslmaths iso2.0_nodif_brain -bin iso2.0_nodif_brain_mask

# reslice mrDWI to isometric
flirt -in pDWI -ref nodif_brain -out iso2.0_pDWI -applyisoxfm 2

