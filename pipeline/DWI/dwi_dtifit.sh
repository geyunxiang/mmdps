#!/bin/bash

# Usage: 
# dtifit -k <filename>
#  dtifit --verbose
#
# Compulsory arguments (You MUST set one or more of):
# 	-k,--data	dti data file
# 	-o,--out	Output basename
# 	-m,--mask	Bet binary mask file
# 	-r,--bvecs	b vectors file
# 	-b,--bvals	b values file
fsl5.0-dtifit -k pDWI -m nodif_brain_mask -r DWI.bvec -b DWI.bval -o dtifitresult


fsl5.0-fslmaths dtifitresult_L1.nii.gz dtifitresult_AD.nii.gz
fsl5.0-fslmaths dtifitresult_L2.nii.gz -add dtifitresult_L3.nii.gz -div 2 dtifitresult_RD.nii.gz
