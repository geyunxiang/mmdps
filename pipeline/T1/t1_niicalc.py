import os
import numpy as np
import nibabel as nib

def calc_region_mean(img, atlasobj, atlasimg):
    timg = atlasimg
    data = img.get_data()
    tdata = timg.get_data()
    regionmeans = np.empty(atlasobj.count)
    # print(data.shape, tdata.shape)
    os.makedirs('t1mean', exist_ok = True)
    for i, region in enumerate(atlasobj.regions):
        regiondots = data[tdata==region]
        regionmean = np.mean(regiondots)
        regionmeans[i] = regionmean
    return regionmeans

def calc_binary_density(img, atlasobj, atlasimg):
    timg = atlasimg
    data = img.get_data()
    tdata = timg.get_data()
    threshold = 0.5
    data[data <= threshold * 255] = 0
    os.makedirs('t1mean', exist_ok = True)
    nib.save(img, 't1mean/thres_{}.nii.gz'.format(threshold))
    data[data > threshold] = 1
    res = np.empty(atlasobj.count)
    for i, region in enumerate(atlasobj.regions):
        regiondots = data[tdata==region]
        regioncount = regiondots.shape[0]
        ndots = np.sum(regiondots)
        res[i] = ndots / regioncount
    return res
    
