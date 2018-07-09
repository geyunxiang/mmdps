function draw_brain_net(nodefile, edgefile, desc, outpath, bnv_mesh, bnv_cfg)
disp(bnv_mesh);

%Brain Net Viewer
%bnv_mesh = 'BrainMesh_ICBM152_smoothed.nv';
%bnv_cfg = 'BrainNet_Option_net.mat';
outpngname = outpath;

%if exist(outpngname, 'file')
%	return
%end

BrainNet_MapCfg(bnv_mesh, nodefile, edgefile, bnv_cfg, outpngname);

close all;
% add_title_to_pic(outpngname, desc);

end




function add_title_to_pic(picname, desc)
fig = imshow(picname);
title(desc, 'Interpreter', 'none');
axis tight;
print(picname, '-r300', '-dpng');
close all;

end

