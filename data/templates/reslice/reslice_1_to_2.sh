
declare -a arr=("brodmann_lr" "brodmann_lrce" "aal")

for i in "${arr[@]}"
do 
    echo "$i"
    inputpath="../"$i"_1"
    echo $inputpath
    outputname=$i"_2"
    fsl5.0-flirt -in $inputpath -ref MNI152_T1_2mm_brain -out $outputname -applyxfm -interp nearestneighbour

done


