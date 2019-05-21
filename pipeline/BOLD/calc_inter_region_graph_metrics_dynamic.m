function calc_inter_region_graph_metrics_dynamic(netpath, outfolder)

[dirpath, name, ext] = fileparts(netpath);

net = csvread(netpath);
net = abs(net);
n = size(net, 1);
net(logical(eye(n))) = 0;

% wd
attr_wd = sum(net, 1);
attr_wd_fname = strrep(name, 'corrcoef', 'inter-region_wd');
attr_wd_fname = [attr_wd_fname, '.csv'];
% attr_wd_fname = 'inter-region_wd.csv';
outpath = fullfile(outfolder, attr_wd_fname);
csvwrite(outpath, attr_wd);

% bc
connet = 1 ./ net;
connet(connet==Inf) = 0;
spconnet = sparse(connet);
attr_bc = betweenness_centrality(spconnet);
attr_wd_fname = strrep(name, 'corrcoef', 'inter-region_bc');
attr_wd_fname = [attr_wd_fname, '.csv'];
% attr_bc_fname = 'inter-region_bc.csv';
outpath = fullfile(outfolder, attr_bc_fname);
csvwrite(outpath, attr_bc');

% ccfs
binnet = net;
binnet_threshold = 0.5;
binnet(binnet > binnet_threshold) = 1;
binnet(binnet <= binnet_threshold) = 0;
spbinnet = sparse(binnet);
attr_ccfs = clustering_coefficients(double(spbinnet));
attr_wd_fname = strrep(name, 'corrcoef', 'inter-region_ccfs');
attr_wd_fname = [attr_wd_fname, '.csv'];
% attr_ccfs_fname = 'inter-region_ccfs.csv';
outpath = fullfile(outfolder, attr_ccfs_fname);
csvwrite(outpath, attr_ccfs');

% le
attr_le = efficiency_wei(net, 1);
attr_wd_fname = strrep(name, 'corrcoef', 'inter-region_le');
attr_wd_fname = [attr_wd_fname, '.csv'];
% attr_le_fname = 'inter-region_le.csv';
outpath = fullfile(outfolder, attr_le_fname);
csvwrite(outpath, attr_le');

end
