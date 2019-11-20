#!/bin/bash

# Pre-processing of DWI. This is the first step.


# subtract b0 image as nodif.nii
# fslroi <input> <output> <tmin> <tsize>
fsl5.0-fslroi DWI nodif 0 1

# bet nodif.nii, output nodif_brain.nii and mask
# bet2 <input_fileroot> <output_fileroot> [options]
# -m,--mask	generate binary brain mask
# -f <f>	fractional intensity threshold (0->1); default=0.5; smaller values give larger brain outline estimates
fsl5.0-bet2 nodif nodif_brain -m -f 0.2

# apply mask to DWI
# fslmaths [-dt <datatype>] <first_input> [operations and inputs] <output> [-odt <datatype>]
# -mas   : use (following image>0) to mask current image
fsl5.0-fslmaths DWI -mas nodif_brain_mask rDWI

# eddy correct
# eddy_correct <4dinput> <4doutput> <reference_no> [<interp>]
fsl5.0-eddy_correct rDWI pDWI 0


