#!/bin/bash



FILEPATH_MNI152_T1_2mm_brain=$MMDPS_ROOTDIR/data/MNI/MNI152_T1_2mm_brain.nii.gz

fsl5.0-flirt -in dtifitresult_MD -ref nodif_brain -out iso2.0_dtifitresult_MD -applyisoxfm 2
fsl5.0-flirt -in dtifitresult_FA -ref nodif_brain -out iso2.0_dtifitresult_FA -applyisoxfm 2

fsl5.0-flirt -in dtifitresult_MD -applyxfm -init normalized_nodif_brain.mat -out normalized_dtifitresult_MD -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain
fsl5.0-flirt -in dtifitresult_FA -applyxfm -init normalized_nodif_brain.mat -out normalized_dtifitresult_FA -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain
