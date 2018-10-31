#!/bin/bash

# Reslice DWI data to isometric
# Input: pre-processed DWI data
# Output: nodif_brain and DWI in isometric


# reslice nodif_brain to isometric
fsl5.0-flirt -in nodif_brain -ref nodif_brain -out iso2.0_nodif_brain -applyisoxfm 2

# generate mask
fsl5.0-fslmaths iso2.0_nodif_brain -bin iso2.0_nodif_brain_mask

# reslice mrDWI to isometric
fsl5.0-flirt -in pDWI -ref nodif_brain -out iso2.0_pDWI -applyisoxfm 2

