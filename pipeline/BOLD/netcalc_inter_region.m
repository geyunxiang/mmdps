function netcalc_inter_region(netpath, outfolder)

net = csvread(netpath);
net = abs(net);
n = size(net, 1);
net(logical(eye(n))) = 0;

% wd
attr_wd = sum(net, 1);
attr_wd_fname = 'inter-region_wd.csv';
outpath = fullfile(outfolder, attr_wd_fname);
csvwrite(outpath, attr_wd);

% bc
connet = 1 ./ net;
connet(connet==Inf) = 0;
spconnet = sparse(connet);
attr_bc = betweenness_centrality(spconnet);
attr_bc_fname = 'inter-region_bc.csv';
outpath = fullfile(outfolder, attr_bc_fname);
csvwrite(outpath, attr_bc');

% ccfs
binnet = net;
binnet_threshold = 0.5;
binnet(binnet > binnet_threshold) = 1;
binnet(binnet <= binnet_threshold) = 0;
spbinnet = sparse(binnet);
attr_ccfs = clustering_coefficients(double(spbinnet));
attr_ccfs_fname = 'inter-region_ccfs.csv';
outpath = fullfile(outfolder, attr_ccfs_fname);
csvwrite(outpath, attr_ccfs');

% le
attr_le = efficiency_wei(net, 1);
attr_le_fname = 'inter-region_le.csv';
outpath = fullfile(outfolder, attr_le_fname);
csvwrite(outpath, attr_le');



end
