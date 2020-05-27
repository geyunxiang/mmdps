#!/bin/bash

# normalized space
# template already in MNI space, just copy and rename
# Example: ./individual_gen_template.sh ../../../commonfiles/brodmann_lr_2.nii.gz brodmann_lr_2

ATLASNAME=$(basename "$PWD")

echo "atlasname: ${ATLASNAME}"

FILEPATH_template=$MMDPS_ROOTDIR/atlas/$ATLASNAME/"${ATLASNAME}_2.nii"
OUTDIRNAME_template=normalizedspace

OUTDIR="$OUTDIRNAME_template"
mkdir -p $OUTDIR

cp $FILEPATH_template "$OUTDIR/wtemplate_2.nii"
gzip -f "$OUTDIR/wtemplate_2.nii"
