#!/bin/bash

# Do register, register iso2.0_nodif_brain to MNI space, get the transform, and then get the inversed transform, which can transform from MNI space to individual space



FILEPATH_MNI152_T1_2mm_brain=$MMDPS_ROOTDIR/data/MNI/MNI152_T1_2mm_brain.nii.gz

# register iso2.0_nodif_brain to MNI space, and get transform matrix
fsl5.0-flirt -in iso2.0_nodif_brain -ref $FILEPATH_MNI152_T1_2mm_brain -out normalized_iso2.0_nodif_brain -omat normalized_iso2.0_nodif_brain.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear

# invert the transform matrix, can transform from MNI 2 to individual 2
fsl5.0-convert_xfm -omat inv_normalized_iso2.0_nodif_brain.mat -inverse normalized_iso2.0_nodif_brain.mat



