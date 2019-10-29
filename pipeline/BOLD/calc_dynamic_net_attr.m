function calc_dynamic_net_attr(rootFolder)

nameList = ls(rootFolder);
atlasList = [string('brodmann_lr'), string('brodmann_lrce'), string('aicha'), string('bnatlas'), string('aal')];
for idx = 3:size(nameList, 1)
	subject = nameList(idx, :);
	for atlasIdx = 1:length(atlasList)
		atlas = atlasList(atlasIdx);
		netattrfolder = strcat(rootFolder, '/', subject, '/', atlas, '/bold_net_attr/dynamic 3 100/');
		netattrfolder = char(netattrfolder);
		if ~exist(netattrfolder, 'file')
			mkdir(netattrfolder);
		end
		netFileList = ls(char(strcat(rootFolder, '/', subject, '/', atlas, '/bold_net/dynamic 3 100/')));
		for m = 1:length(netFileList)
			filename = netFileList(m, :);
			if ~any(strfind(filename, 'corrcoef'))
				continue
			end
			% netpath = fullfile('bold_net', netfilename);
			netpath = char(strcat(rootFolder, '/', subject, '/', atlas, '/bold_net/dynamic 3 100/', filename));
% 			netcalc_inter_region(netpath, netattrfolder);
            fprintf(1, '%s\n', netpath);
		end
	end
end
% niipath = '../pBOLD.nii';
% template = get_template(templatename);
% templatepath = template.niipath;

% netcalc_intra_region(niipath, netattrfolder, templatepath);
end