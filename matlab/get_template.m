function template = get_template(templatename)
t = {};

thisfilepath = mfilename('fullpath');
[mmdpsmatlab, name, ext] = fileparts(thisfilepath);
[mmdpsroot, name, ext] = fileparts(mmdpsmatlab);

atlasfolder = fullfile(mmdpsroot, 'atlas');

niirp = [templatename, '_3.nii'];
fprintf(1, 'Template file: %s\n', niirp);

t.niipath = fullfile(atlasfolder, templatename, niirp);

template = t;
end
