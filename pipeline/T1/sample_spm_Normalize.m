%-----------------------------------------------------------------------
% Job saved on 10-Jan-2017 13:27:39 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (6470)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.spm.spatial.normalise.estwrite.subj.vol = {'T1.nii,1'};
matlabbatch{1}.spm.spatial.normalise.estwrite.subj.resample = {'c123T1.nii,1'};
matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.biasreg = 0.0001;
matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.biasfwhm = 60;
matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.tpm = {fullfile(spm('Dir'), 'tpm', 'TPM.nii')};
matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.affreg = 'mni';
matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.reg = [0 0.001 0.5 0.05 0.2];
matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.fwhm = 0;
matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.samp = 3;
matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.bb = [-90 -125 -71
                                                             90 91 109];
matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.vox = [1 1 1];
matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.interp = 4;
