#!/bin/bash

# Pre-processing of DWI. This is the first step.


# subtract b0 image as nodif.nii
fsl5.0-fslroi DWI nodif 0 1

# bet nodif.nii, output nodif_brain.nii and mask
fsl5.0-bet2 nodif nodif_brain -m -f 0.2

# apply mask to DWI
fsl5.0-fslmaths DWI -mas nodif_brain_mask rDWI

# eddy correct
fsl5.0-eddy_correct rDWI pDWI 0


