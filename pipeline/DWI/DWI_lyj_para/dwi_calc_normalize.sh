#!/bin/bash

# Do normalization, normalize nodif_brain and DWI data to MNI space


# FILEPATH_MNI152_T1_2mm_brain=../MNI152_T1_2mm.nii.gz
FILEPATH_MNI152_T1_2mm_brain=$MMDPS_ROOTDIR/data/MNI/MNI152_T1_2mm_brain.nii.gz


# normalize nodif_brain to normalized_nodif_brain, get the transform
# flirt [options] -in <inputvol> -ref <refvol> -omat <outputmatrix>
# -omat <matrix-filename>            (output in 4x4 ascii format)
# -bins <number of histogram bins>   (default is 256)
# -cost {mutualinfo,corratio,normcorr,normmi,leastsq,labeldiff,bbr}        (default is corratio)
# -searchrx <min_angle> <max_angle>  (angles in degrees: default is -90 90)
# -searchry <min_angle> <max_angle>  (angles in degrees: default is -90 90)
# -searchrz <min_angle> <max_angle>  (angles in degrees: default is -90 90)
# -dof  <number of transform dofs>   (default is 12)
# -interp {trilinear,nearestneighbour,sinc,spline}  (final interpolation: def - trilinear)

# flirt -in pDWI -ref ../MNI152_T1_2mm -out normalized_nodif_brain -omat normalized_nodif_brain.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear
flirt -in pDWI -ref $FILEPATH_MNI152_T1_2mm_brain -out normalized_nodif_brain -omat normalized_nodif_brain.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear


# generate mask
fslmaths normalized_nodif_brain -bin normalized_mask

# the nodif_brain is aligned with mrDWI, apply the normalization transform to mrDWI, get normalized_mrDWI.nii.gz
# -applyxfm                          (applies transform (no optimisation) - requires -init)

# flirt -in pDWI -applyxfm -init normalized_nodif_brain.mat -out normalized_pDWI -paddingsize 0.0 -interp trilinear -ref ../MNI152_T2_2mm
flirt -in pDWI -applyxfm -init normalized_nodif_brain.mat -out normalized_pDWI -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain





