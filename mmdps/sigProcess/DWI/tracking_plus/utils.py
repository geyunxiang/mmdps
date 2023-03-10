
from dipy.io.image import load_nifti, load_nifti_data, save_nifti
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
import dipy.tracking.utils as util
from dipy.tracking.streamline import Streamlines
import numpy as np


# read DWI, brain mask, bval, bvec
def get_data(data_path=None,
             norm='normalized_pDWI.nii.gz', bval='DWI.bval', bvec='DWI.bvec',
             mask='normalized_mask.nii.gz', FA='FA.nii.gz'):

    root = data_path
    DWI = root+'/'+norm
    bvals_path = root+'/'+bval
    bvecs_path = root+'/'+bvec
    mask_path = root+'/'+mask


    DWI_data, affine, img = load_nifti(DWI, return_img=True)

    bvals, bvecs = read_bvals_bvecs(bvals_path, bvecs_path)
    gtab = gradient_table(bvals, bvecs)
    head_mask = load_nifti_data(mask_path)

    if FA != None:
        FA_path = root + '/' + FA
        FA = load_nifti_data(FA_path)
        return DWI_data, affine, img, gtab, head_mask, FA
    else:
        return DWI_data, affine, img, gtab, head_mask


# fit the DWI data into DTI model, save FA file and return FA, MD, GA, RD, AD
def dwi_dtifit(data_path=None, norm='normalized_pDWI', bval='DWI.bval', bvec='DWI.bvec',
             mask='normalized_mask', return_FA=False, save_FA=True, save_FA_path=None, FA_file_name=None):


    DWI_data, affine, img, gtab, head_mask = get_data(data_path=data_path,
                                                      norm=norm, bval=bval, bvec=bvec,
                                                      mask=mask, FA=None)


    tenmodel = dti.TensorModel(gtab)
    tenfit = tenmodel.fit(DWI_data)

    FA = (tenfit.fa)*head_mask
    MD = (tenfit.md)*head_mask
    GA = (tenfit.ga)*head_mask
    RD = (tenfit.rd)*head_mask
    AD = (tenfit.ad)*head_mask

    if save_FA:
        if save_FA_path == None:
            save_FA_path = data_path
        if FA_file_name == None:
            FA_file_name = 'FA.nii.gz'
        save_nifti(fname=save_FA_path+'/'+FA_file_name, data=FA, affine=affine)
    if return_FA:
        return FA, MD, GA, RD, AD

# reduct the streamlines by length threshold
# in the functions below, the input paramter affine should be detmermined by the space of the streamlines
# affine = np.eye(4) if streamlines in voxel space
# voxel space if load from .trk, need:
# tracks=load_trk('trackfile.trk')
# tracks.to_vox()
# streamlines = tracks.streamlines

def reduct(streamlines, threshold=1):

    new_streamlines = []

    for i in range(len(streamlines)):

        line = np.round(streamlines[i]).astype(np.intp)

        if line.shape[0] > threshold:
            new_streamlines.append(line)

    return new_streamlines

#return the number of streamlines that go through/not go through ROI

def cal_ROI_num(ROI_mask, streamlines, GetThrough=True,
                return_streamlines=False, return_number=True,affine=None):

    streamlines=reduct(streamlines)
    ROI_streamlines = util.target(streamlines, affine=affine, target_mask=ROI_mask.astype(np.float), include=GetThrough)

    if return_streamlines:
        return Streamlines(ROI_streamlines)
    elif return_number:
        return len(Streamlines(ROI_streamlines))


#return the number list of streamlines that go through ROI for atlas

def ROI_atlas(streamlines, atlas, affine=None):


    index_max = np.max(atlas)
    index_min = np.min(atlas)
    roi_number = np.zeros(index_max-index_min+1)

    for i in range(index_min, index_max + 1):
        ROI_mask = atlas == i

        roi_number[i]=cal_ROI_num(ROI_mask=ROI_mask, streamlines=streamlines, affine=affine)
        #print('ROI', i, 'finished!')

    #print('finished exctracting features!')

    return roi_number

# return the connectivity matrix for atlas

def track_gen_net_work(atlas, streamlines=None, affine=None):


    labels = atlas.astype('int')
    streamlines=reduct(streamlines)

    M, grouping = util.connectivity_matrix(streamlines, affine=affine, label_volume = labels,
                              return_mapping=True, mapping_as_streamlines=True)

    return M

#streamlines in voxal space, return mean length and Standard Deviation

def average_length(streamlines=None, mask=None):

    if mask==None:
        pass
    else:
        streamlines = ROI_streamlines = util.target(streamlines, affine=np.eye(4), target_mask=mask.astype(np.float), include=True)

    leng=np.array(list(length(streamlines)))

    return np.mean(leng), np.sqrt(np.var(leng))

# return average values, remove 0 and np.nan
def average_values(value=None, mask=None):

    if mask==None:
        pass
    else:
        value=value*mask

    value[value==np.nan]=0

    return np.sum(value)/(np.sum(value!=0))

