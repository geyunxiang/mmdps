%-----------------------------------------------------------------------
% Job saved on 10-Jan-2017 13:20:09 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (6470)
% cfg_basicio BasicIO - Unknown
% Function: use c1T1/c2T1/c3T1 to generate a mask, and strip the skull in T1
%			the input data is the original T1.nii, rather than mT1.nii
% Output:	T1_brain.nii 		Skull stripped T1 (in T1 Native Space)
%-----------------------------------------------------------------------
matlabbatch{1}.spm.util.imcalc.input = {
                                        'c1T1.nii,1'
                                        'c2T1.nii,1'
                                        'c3T1.nii,1'
                                        'T1.nii,1'
                                        };
matlabbatch{1}.spm.util.imcalc.output = 'T1_brain.nii';
matlabbatch{1}.spm.util.imcalc.outdir = {''};
matlabbatch{1}.spm.util.imcalc.expression = 'i4 .* ((i1 + i2 + i3) > 0.5)';
matlabbatch{1}.spm.util.imcalc.var = struct('name', {}, 'value', {});
matlabbatch{1}.spm.util.imcalc.options.dmtx = 0;
matlabbatch{1}.spm.util.imcalc.options.mask = 0;
matlabbatch{1}.spm.util.imcalc.options.interp = 1;
matlabbatch{1}.spm.util.imcalc.options.dtype = 4; % signed short
