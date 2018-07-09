#!/bin/bash

# Do normalization, normalize nodif_brain and DWI data to MNI space


FILEPATH_MNI152_T1_2mm_brain=$MMDPS_ROOTDIR/data/MNI/MNI152_T1_2mm_brain.nii.gz



# normalize nodif_brain to normalized_nodif_brain, get the transform
fsl5.0-flirt -in pDWI -ref $FILEPATH_MNI152_T1_2mm_brain -out normalized_nodif_brain -omat normalized_nodif_brain.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear

# generate mask
fsl5.0-fslmaths normalized_nodif_brain -bin normalized_mask

# the nodif_brain is aligned with mrDWI, apply the normalization transform to mrDWI, get normalized_mrDWI.nii.gz
fsl5.0-flirt -in pDWI -applyxfm -init normalized_nodif_brain.mat -out normalized_pDWI -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain




