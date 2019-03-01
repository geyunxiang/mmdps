function run_spm_jobs(spmjobfiles)

disp('--start spm jobs--');

spm('defaults', 'fmri');
spm_jobman('initcfg');

for i = 1:length(spmjobfiles)
	jobfile = spmjobfiles{i};
	jobfilepath = which(jobfile);
	disp(jobfilepath);
	if isempty(jobfilepath)
		disp(['cannot find file: ', jobfile]);
		return
	end
	spm_jobman('run', jobfilepath);
end

disp('--end spm jobs--');

end
