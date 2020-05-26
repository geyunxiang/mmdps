import numpy as np
import nibabel as nib

def multiply_one_many(dataone, datamany):
    res = np.zeros(datamany.shape)
    lastdim = res.shape[-1]
    for i in range(lastdim):
        res[:, :, :, i] = dataone * datamany[:, :, :, i]
    return res

def floatcolor3_to_int24rgb(rgb_float):
    rgb_arr = np.array(255.0 * rgb_float, 'uint8')
    rgb_dtype = np.dtype([('R', 'u1'), ('G', 'u1'), ('B', 'u1')])
    shape_3d = rgb_arr.shape[:-1]
    rgb_arr_typed = rgb_arr.view(rgb_dtype).reshape(shape_3d)
    return rgb_arr_typed

def nifti_noext(niifilename):
    if niifilename[-3:] == '.gz':
        resname = niifilename[:-7]
    else:
        resname = niifilename[:-3]
    return resname

def to_fa_color(niifa, niiv1):
    fa_img = nib.load(niifa)
    v1_img = nib.load(niiv1)  # [-1, 1] for each component

    fa_data = fa_img.get_fdata()
    v1_data = np.abs(v1_img.get_fdata())
    print('dwi_ditfit_fa_add_color, fa_data.shape: ', fa_data.shape)
    print('dwi_ditfit_fa_add_color, v1_data.shape: ', v1_data.shape)

    fa_color_float = multiply_one_many(fa_data, v1_data)
    print('dwi_ditfit_fa_add_color, fa_color_float.shape: ', fa_color_float.shape)
    print('dwi_ditfit_fa_add_color, fa_color_float[111, 160, 41, 1]: ', fa_color_float[111, 160, 41, 1])

    fa_color_data = floatcolor3_to_int24rgb(fa_color_float)
    print('dwi_ditfit_fa_add_color, fa_color_data.shape: ', fa_color_data.shape)

    fa_color_int24_img = nib.Nifti1Image(fa_color_data, fa_img.get_affine())

    namenoext = nifti_noext(niifa)
    outfilename = namenoext + '_color.nii.gz'
    nib.save(fa_color_int24_img, outfilename)

if __name__ == '__main__':
    to_fa_color('dtifitresult_FA.nii.gz', 'dtifitresult_V1.nii.gz')
