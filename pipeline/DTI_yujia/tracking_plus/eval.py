import matplotlib
import matplotlib.pyplot as plt
import dipy.tracking.streamline
import dipy.tracking.life as life
#from dipy.viz import window, actor, colormap as cmap
import numpy as np
import os.path as op
from dipy.io.streamline import load_trk
from dipy.io.image import save_nifti
import dipy.core.optimize as opt
import argparse
import json
import os

def reduct(streamlines, data):

    new_streamlines = []
    for i in range(len(streamlines)):
        line = streamlines[i]
        line = np.round(line).astype(np.intp)

        flag = 0

        if line.shape[0] > 1:

            for j in range(line.shape[0]):

                if data[line[j, 0], line[j, 1], line[j, 2]] == 0:
                    flag = 1
                    break
            if flag == 0:
                new_streamlines.append(line)

    return new_streamlines



def eval_method(name=None, method=None, track_path=None, data_path=None):

    if track_path==None:
        track_path='./Result/Track/tractogram_'+method+'_'+name+'.trk'
    if data_path==None:
        data_path='./data/DWI/'+name+'/'


    if not op.exists(track_path):
        print('no tracking')
        return 0

    else:

        from dipy.io.gradients import read_bvals_bvecs
        from dipy.io.image import load_nifti_data, load_nifti
        from dipy.core.gradients import gradient_table

        data, affine, hardi_img = load_nifti(data_path+'norm.nii.gz', return_img=True)
        print(data.shape)
        labels = load_nifti_data(data_path+'seg.nii.gz')
        # t1_data = load_nifti_data('./data/tanenci_20170601/b0.nii.gz')
        bvals, bvecs = read_bvals_bvecs(data_path+'DWI.bval',data_path+'DWI.bvec')
        gtab = gradient_table(bvals, bvecs)



# Read the candidates from file in voxel space:
    candidate_sl_sft = load_trk(track_path, 'same', bbox_valid_check=False)
    candidate_sl_sft.to_vox()
    candidate_sl = candidate_sl_sft.streamlines

    print('loading finished, begin weighting')

    fiber_model = life.FiberModel(gtab)
    inv_affine = np.linalg.inv(hardi_img.affine)
    fiber_fit = fiber_model.fit(data, reduct(candidate_sl, data[:, :, :, 0]), affine=np.eye(4))

    print('weighting finished, begin prediction')

    beta_baseline = np.zeros(fiber_fit.beta.shape[0])
    pred_weighted = np.reshape(opt.spdot(fiber_fit.life_matrix, beta_baseline),
                               (fiber_fit.vox_coords.shape[0],
                                np.sum(~gtab.b0s_mask)))


    model_predict = fiber_fit.predict()
    model_error = model_predict - fiber_fit.data
    model_rmse = np.sqrt(np.mean(model_error[:, 10:] ** 2, -1))
    #print('model_rmse:', model_rmse.shape)

    vol_model = np.zeros(data.shape[:3])* np.nan
    vol_model[fiber_fit.vox_coords[:, 0],
              fiber_fit.vox_coords[:, 1],
              fiber_fit.vox_coords[:, 2]] = model_rmse



    #print('error:', np.sum(vol_model) / model_rmse.shape[0])


    return np.sum(model_rmse)/model_rmse.shape[0], vol_model, affine





if __name__ == '__main__':



    parser = argparse.ArgumentParser(description="evaluation of different tracking methods")
    parser.add_argument('-p', '--data_path', default=None, help='data_path')
    parser.add_argument('-n', '--name', default=None, help='name of individual')
    parser.add_argument('-o', '--output_path', default='./Result/eval', help='output_path')
    parser.add_argument('-m', '--method', type=int, default=1, help='1:EuDX; 2:Probabilistic; 3:Deterministic')
    parser.add_argument('-t', '--track_path', default=None, help='track_path')

    args = parser.parse_args()
    print(args)

    data_path = args.data_path
    name = args.name
    output_path = args.output_path
    method_index = args.method
    track_path = args.track_path

    if method_index == 1:
        method = 'EuDX'
    elif method_index == 2:
        method = 'probabilistic'
    elif method_index == 3:
        method = 'deterministic'
    elif method_index == 4:
        method = 'sfm'
    elif method_index == 5:
        method = 'pft'
    else:
        method = None

    mean_error, vol_model, affine = eval_method(name=name, method=method, track_path=track_path, data_path=data_path)
    print(method, name, 'error:', mean_error)



    save_nifti(output_path+'/'+name+'_'+method+'_eval.nii.gz', vol_model, affine)

    if not os.path.isfile(output_path+'/eval.json'):
        mode = 'w+'
    else:
        mode = 'r+'

    with open(output_path+'/eval.json', mode) as fileR:  # 打开文本读取状态

        strF = fileR.read()
        #print(len(strF))
        if len(strF) == 0:
            R = {}

        else:

            R = json.loads(strF)  # 解析读到的文本内容 转为python数据 以一个变量接收

        #print(args.name in R.keys())

        if args.name in R.keys():
            a = R[args.name]
            a[method] = mean_error
            R[args.name] = a
        else:
            a = {method:mean_error}
            R[args.name] = a

    with open(output_path+'/eval.json', 'w') as fileR:

        jsObj = json.dumps(R, indent=4)
        fileR.write(jsObj)




