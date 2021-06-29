#!/bin/bash



FILEPATH_MNI152_T1_2mm_brain=$MMDPS_ROOTDIR/data/MNI/MNI152_T1_2mm_brain.nii.gz

flirt -in dtifitresult_MD -ref nodif_brain -out iso2.0_dtifitresult_MD -applyisoxfm 2
flirt -in dtifitresult_FA -ref nodif_brain -out iso2.0_dtifitresult_FA -applyisoxfm 2

flirt -in dtifitresult_AD -ref nodif_brain -out iso2.0_dtifitresult_AD -applyisoxfm 2
flirt -in dtifitresult_RD -ref nodif_brain -out iso2.0_dtifitresult_RD -applyisoxfm 2

flirt -in dtifitresult_MD -applyxfm -init normalized_nodif_brain.mat -out normalized_dtifitresult_MD -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain
flirt -in dtifitresult_FA -applyxfm -init normalized_nodif_brain.mat -out normalized_dtifitresult_FA -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain
flirt -in dtifitresult_AD -applyxfm -init normalized_nodif_brain.mat -out normalized_dtifitresult_AD -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain
flirt -in dtifitresult_RD -applyxfm -init normalized_nodif_brain.mat -out normalized_dtifitresult_RD -paddingsize 0.0 -interp trilinear -ref $FILEPATH_MNI152_T1_2mm_brain
