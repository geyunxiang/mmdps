%-----------------------------------------------------------------------
% Job saved on 10-Jan-2017 13:20:09 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (6470)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.spm.util.imcalc.input = {
                                        'c1T1.nii,1'
                                        'c2T1.nii,1'
                                        'c3T1.nii,1'
                                        'T1.nii,1'
                                        };
matlabbatch{1}.spm.util.imcalc.output = 'c123T1.nii';
matlabbatch{1}.spm.util.imcalc.outdir = {''};
matlabbatch{1}.spm.util.imcalc.expression = 'i4 .* ((i1 + i2 + i3) > 0.5)';
matlabbatch{1}.spm.util.imcalc.var = struct('name', {}, 'value', {});
matlabbatch{1}.spm.util.imcalc.options.dmtx = 0;
matlabbatch{1}.spm.util.imcalc.options.mask = 0;
matlabbatch{1}.spm.util.imcalc.options.interp = 1;
matlabbatch{1}.spm.util.imcalc.options.dtype = 4;
