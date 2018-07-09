function netcalc_inter_region(niipath, outfolder, templatepath)
	if ~isdir(outfolder)
		mkdir(outfolder);
	end
	
	template_vol = load_nii(templatepath);
	template_img = template_vol.img;
	template_size = size(template_img);
	template_long = reshape(template_img, prod(template_size), 1);
	
	thenii = load_nii(niipath);
	theimg = thenii.img;
	theimg_size = size(theimg);
	theimg_long = reshape(theimg, theimg_size(1)*theimg_size(2)*theimg_size(3), theimg_size(4));
	
    weakstrong = 'strong';
    netthreshold = 0.5;

    regions =unique(template_long);
    regions=regions(2:end);
    region_num = length(regions);
    CC = zeros(1, region_num);
    CCFS = zeros(1, region_num);
    BC = zeros(1, region_num);
    PATH = zeros(1, region_num);


    parfor Network_Num = 1:region_num
        % Compute the regional network
        Regional_Data = double(theimg_long(template_long == regions(Network_Num), :));
        if isempty(Regional_Data)
            continue;
        end
        Temp = Regional_Data;
        PP = 0;
        for i = 1:size(Temp, 1)
            if(sum(abs(Temp(i, :)))==0)
                PP = [PP, i];
            end
        end
        if(size(PP, 2)>1)
            Regional_Data(PP(2:size(PP, 2)), :) = [];
        end
        Cor = corrcoef(Regional_Data');
        Cor = abs(Cor);
        Size = size(Cor, 1);
        for i = 1:Size
            Cor(i, i) = 0;
        end
        Cor1 = Cor;

        if strcmp(weakstrong, 'strong')
            %strong
            for i = 1:Size %slow
                for m = 1:Size
                    if(Cor1(i, m)<netthreshold)
                        Cor1(i, m) = 0;
                    else
                        Cor1(i, m) = Cor1(i, m);
                    end
                end
            end 
        else
            %weak
            for i = 1:Size %slow
                for m = 1:Size
                    if(Cor1(i, m)>netthreshold)
                        Cor1(i, m) = 0;
                    else
                        Cor1(i, m) = Cor1(i, m);
                    end
                end
            end 
        end

        Cor1 = sparse(Cor1);
        % Compute the network features
        %  c= mean(mean(atanh(Cor)*sqrt(D-3), 1));
        c = efficiency_wei(Cor,0); %very very slow
        ccfs= mean(clustering_coefficients(double(Cor1>0))); %kindof slow
        Net = zeros(size(Cor, 1),Size);
        for i = 1:Size %slow
            for m = 1:Size
                if(Cor(i, m) ~= 0)
                    Net(i, m) = 1/Cor(i, m);
                end
            end
        end
        Net = sparse(Net);
        bc = mean(betweenness_centrality(Net)); %slow
        path1 = all_shortest_paths(Net); %kindof slow
        path = sum(sum(path1))/Size/(Size-1);

        CC( Network_Num) = c;
        CCFS( Network_Num) = ccfs;
        BC( Network_Num) = bc;
        PATH( Network_Num) = path;
    end
	
	
	outpath = fullfile(outfolder, 'intra-region_ge.csv');
	csvwrite(outpath, CC);
	outpath = fullfile(outfolder, 'intra-region_ccfs.csv');
	csvwrite(outpath, CCFS);
	outpath = fullfile(outfolder, 'intra-region_bc.csv');
	csvwrite(outpath, BC);
	outpath = fullfile(outfolder, 'intra-region_path.csv');
	csvwrite(outpath, PATH);

	
	
	
end


