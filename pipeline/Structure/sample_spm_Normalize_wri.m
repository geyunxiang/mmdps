%-----------------------------------------------------------------------
% Job saved on 10-Jan-2017 13:27:39 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (6470)
% cfg_basicio BasicIO - Unknown
% Function: use Deformation Field from Segmentation to normalize T1_brain.nii
%			the output is in MNI Space.
% Output: wT1_brain.nii 		Skull stripped T1 image in MNI Space
%-----------------------------------------------------------------------
matlabbatch{1}.spm.spatial.normalise.write.subj.def = {'y_T1.nii'}; % deformation field
matlabbatch{1}.spm.spatial.normalise.write.subj.resample = {'T1_brain.nii,1'};
matlabbatch{1}.spm.spatial.normalise.write.woptions.bb = [-90 -125 -71
                                                             90 91 109];
matlabbatch{1}.spm.spatial.normalise.write.woptions.vox = [1 1 1];
matlabbatch{1}.spm.spatial.normalise.write.woptions.interp = 4;
matlabbatch{1}.spm.spatial.normalise.write.woptions.prefix = 'w';