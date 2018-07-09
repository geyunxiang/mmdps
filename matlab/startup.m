thisfilepath = mfilename('fullpath');
[mmdpsmatlab, name, ext] = fileparts(thisfilepath);
[mmdpsroot, name, ext] = fileparts(mmdpsmatlab);
addpath(fullfile(mmdpsroot, 'pipeline/T1'));
addpath(fullfile(mmdpsroot, 'pipeline/BOLD'));

