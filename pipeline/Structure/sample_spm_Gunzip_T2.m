%-----------------------------------------------------------------------
% Job saved on 09-Jan-2017 17:27:02 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (6470)
% cfg_basicio BasicIO - Unknown
% Function: unzip .nii.gz file, output .nii file
% Output: T2_brain.nii 		T2 bet data
%-----------------------------------------------------------------------
matlabbatch{1}.cfg_basicio.file_dir.file_ops.cfg_gunzip_files.files = {'T2_brain.nii.gz'};
