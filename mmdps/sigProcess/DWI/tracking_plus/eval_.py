
import mmdps.sigProcess.DWI.tracking_plus.life_ as life_
import dipy.tracking.life as life
import numpy as np
import dipy.core.optimize as opt
from dipy.reconst.csdeconv import auto_response_ssst

from  mmdps.sigProcess.DWI.tracking_plus.utils import reduct

## return engine vectors and index map

def get_evals_map(gtab, data, head_mask, FA, FA_th=0.15, loc_range=2):

    #pdb.set_trace()
    values = np.zeros((data.shape[0], data.shape[1], data.shape[2], 3))
    loc = np.where((head_mask*(FA>FA_th) != 0))
    row = loc[0]
    col = loc[1]
    z = loc[2]

    mark = np.zeros_like(data[:, :, :, 0])
    mark_index = np.zeros_like(data[:, :, :, 0])
    index = 0
    #pdb.set_trace()

    for i in range(row.shape[0]):

        if mark[row[i], col[i], z[i]] == 0:
            #pdb.set_trace()
            response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.1,
                                                 roi_center=[row[i], col[i], z[i]])
            #pdb.set_trace()

            mark[row[i] -loc_range :row[i] + loc_range, col[i] - loc_range:col[i] + loc_range, z[i] - loc_range:z[i] + loc_range] = 1
            mark_index[row[i] - loc_range:row[i] + loc_range, col[i] - loc_range:col[i] + loc_range, z[i] - loc_range:z[i] + loc_range] = index

            values[row[i], col[i], z[i]] = response[0]
            print('{}/{} finished!'.format(i, row.shape[0]) )
    #pdb.set_trace()


    return values*(np.expand_dims(head_mask>0,3).repeat(3,axis=3)), mark_index*(head_mask>0)




def get_percentage(error, data):

    p = np.ones_like(data[:,:,:,0])*np.nan

    for i in range(0, data.shape[0]):
        for j in range(0, data.shape[1]):
            for k in range(0, data.shape[2]):


                if (data[i, j, k, 1:]>1).all():

                    error_percentage = error[i, j, k, :]/data[i, j, k, 1:]
                    rmse = np.mean(np.absolute(error_percentage))

                    p[i, j, k] = rmse

    return p


def get_new_life_error(error, data, gtab, direction_map):

    # input error, numpy array: [x, y, z, d-1]
    # return numpy array: [x, y, z, d-1]

    new_error = np.ones_like(data[:,:,:,1:]) * np.nan

    for i in range(0, data.shape[0]):
        for j in range(0, data.shape[1]):
            for k in range(0, data.shape[2]):


                if np.any(np.isnan(error[i, j, k, :])) and np.all(data[i, j, k, :]!=0):


                    bvecs = gtab.bvecs[~gtab.b0s_mask]
                    bvals = gtab.bvals[~gtab.b0s_mask]
                    tensor = direction_map[i, j, k, :]

                    ADC = -np.mean(np.log(data[i,j,k,1:]/data[i,j,k,0]))

                    pred = np.exp(-abs(ADC))*data[i, j, k, 0]

                    error2 = data[i, j, k, 1:] - pred
                    new_error[i, j, k, :] = error2

                elif np.all(data[i, j, k, :]!=0):
                    new_error[i, j, k, :] = error[i, j, k, :]

    return new_error

#LiFE_new, fiber and tissue, percentage

def LiFE_new(streamlines=None, gtab=None, data=None,
                  eval_map=None):


    fiber_model = life_.FiberModel(gtab)
    streamlines = reduct(streamlines)
    fiber_fit = fiber_model.fit(data, streamlines, affine=np.eye(4), sphere=False, evals_map=eval_map[:,:,:,0])

    model_predict = fiber_fit.predict()
    model_error = model_predict - fiber_fit.data

    a = model_error.copy()

    b = np.ones_like(data)*np.nan
    b[fiber_fit.vox_coords[:, 0],
      fiber_fit.vox_coords[:, 1],
      fiber_fit.vox_coords[:, 2], :] = a

    b = b[:, :, :, 1:]

    return get_percentage(error=get_new_life_error(error=b, data=data, gtab=gtab), data=data)

#LiFE, fiber, absolute

def LiFE(streamlines=None, gtab=None, data=None):

    fiber_model = life.FiberModel(gtab)
    streamlines = reduct(streamlines)
    fiber_fit = fiber_model.fit(data, streamlines, affine=np.eye(4), sphere=False)

    model_predict = fiber_fit.predict()
    model_error = model_predict - fiber_fit.data

    a = model_error.copy()

    model_rmse = np.sqrt(np.mean(a[:, :] ** 2, -1))
    vol_model = np.ones(data.shape[:3]) * np.nan
    vol_model[fiber_fit.vox_coords[:, 0],
              fiber_fit.vox_coords[:, 1],
              fiber_fit.vox_coords[:, 2]] = model_rmse

    return vol_model


