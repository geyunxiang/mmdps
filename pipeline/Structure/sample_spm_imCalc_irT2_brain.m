%-----------------------------------------------------------------------
% Job saved on 26-Dec-2018 20:49:07 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (6470)
% cfg_basicio BasicIO - Unknown
% Function: remove negative value in voxels
% Output: irT2_brain.nii 		
%-----------------------------------------------------------------------
matlabbatch{1}.spm.util.imcalc.input = {'rT2_brain.nii,1'};
matlabbatch{1}.spm.util.imcalc.output = 'irT2_brain';
matlabbatch{1}.spm.util.imcalc.outdir = {''};
matlabbatch{1}.spm.util.imcalc.expression = 'i1 .* (i1 > 0)';
matlabbatch{1}.spm.util.imcalc.var = struct('name', {}, 'value', {});
matlabbatch{1}.spm.util.imcalc.options.dmtx = 0;
matlabbatch{1}.spm.util.imcalc.options.mask = 0;
matlabbatch{1}.spm.util.imcalc.options.interp = 1;
matlabbatch{1}.spm.util.imcalc.options.dtype = 2;
