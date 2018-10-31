
netattrfolder = 'bold_net_attr';
if ~exist(netattrfolder, 'file')
	mkdir(netattrfolder);
end

[scanpath, templatename, ext] = fileparts(pwd);

netfilename = 'corrcoef.csv';
netpath = fullfile('bold_net', netfilename);

netcalc_inter_region(netpath, netattrfolder);

niipath = '../pBOLD.nii';
template = get_template(templatename);
templatepath = template.niipath;

netcalc_intra_region(niipath, netattrfolder, templatepath);

