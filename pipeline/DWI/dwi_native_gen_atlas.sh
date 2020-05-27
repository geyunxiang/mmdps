#!/bin/bash

# individual space
# apply inv transform, transform template in MNI to template in individual
# Example: ./individual_gen_template.sh ../../../commonfiles/brodmann_lr_2.nii.gz brodmann_lr_2

ATLASNAME=$(basename "$PWD")
echo "atlasname: ${ATLASNAME}"

FILEPATH_template=$MMDPS_ROOTDIR/atlas/$ATLASNAME/"${ATLASNAME}_2.nii"
OUTDIRNAME_template=nativespace

OUTDIR="$OUTDIRNAME_template"
mkdir -p $OUTDIR

# apply inv transform to template in MNI2, obtain template in person 2
flirt -in $FILEPATH_template -applyxfm -init ../inv_normalized_iso2.0_nodif_brain.mat -out "$OUTDIR/wtemplate_2" -paddingsize 0.0 -interp nearestneighbour -ref ../iso2.0_nodif_brain

