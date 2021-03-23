from dipy.core.gradients import gradient_table
from dipy.data import get_fnames
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti, load_nifti_data
from dipy.reconst.csdeconv import ConstrainedSphericalDeconvModel, auto_response_ssst
from dipy.tracking import utils
from dipy.tracking.local_tracking import LocalTracking, ParticleFilteringTracking
from dipy.tracking.streamline import Streamlines
from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion, CmcStoppingCriterion
#from dipy.viz import window, actor, colormap, has_fury

from dipy.io.stateful_tractogram import Space, StatefulTractogram
from dipy.io.streamline import save_trk
from dipy.data import small_sphere, default_sphere, get_sphere
from dipy.reconst.shm import CsaOdfModel
from dipy.reconst import sfm
from dipy.direction import ProbabilisticDirectionGetter, DeterministicMaximumDirectionGetter, ClosestPeakDirectionGetter, BootDirectionGetter
import numpy as np
# from tracking_plus.ROI import reduct_seed_ROI, minus_ROI
from pipeline.DTI_yujia.tracking_plus.ROI import reduct_seed_ROI, minus_ROI

import time

def get_data(name=None, data_path=None, pft=False, norm='norm.nii.gz', bval='DWI.bval', bvec='DWI.bvec', seg='seg.nii.gz', FA=None, mask='norm_mask.nii.gz'):
    if name != None:
        root = './data/DWI/'+name
    else:
        root = data_path
    DWI = root+'/'+norm
    bvals_path = root+'/'+bval
    bvecs_path = root+'/'+bvec

    mask_path = root+'/'+mask

    data, affine, img = load_nifti(DWI,return_img=True)
    if seg == None:
        labels = None
    else:
        seg_path = root + '/' + seg
        labels = load_nifti_data(seg_path)

    bvals, bvecs = read_bvals_bvecs(bvals_path, bvecs_path)
    gtab = gradient_table(bvals, bvecs)
    head_mask = load_nifti_data(mask_path)

    if not pft:
        return data, affine, img, labels, gtab, head_mask
    else:
        f_pve_csf=root+'./pve_2.nii.gz'
        f_pve_gm=root+'./pve_0.nii.gz'
        f_pve_wm=root+'./pve_1.nii.gz'
        pve_csf_data = load_nifti_data(f_pve_csf)
        pve_gm_data = load_nifti_data(f_pve_gm)
        pve_wm_data, _, voxel_size = load_nifti(f_pve_wm, return_voxsize=True)

        return data, affine, img, labels, gtab, head_mask, \
               pve_csf_data, pve_gm_data, pve_wm_data, voxel_size

def index_transform(method_name=None, method_index=None):
    method = {1:'EuDX', 2:'probabilistic', 3:'deterministic', 4:'sfm'}
    method_ = {'EuDX':1, 'probabilistic':2, 'deterministic':3, 'sfm':4}

    if method_name != None:
        return method_[method_name]
    elif method_index!= None:
        return method[method_index]

def probal(Threshold=.2, data_list=None, seed='.', one_node=False, two_node=False):
    time0 = time.time()
    print("begin loading data, time:", time.time() - time0)

    data = data_list['DWI']
    affine = data_list['affine']
    img = data_list['img']
    labels = data_list['labels']
    gtab = data_list['gtab']
    head_mask = data_list['head_mask']

    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (labels == 2) * (head_mask == 1)

    white_matter = (labels == 2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    print("begin reconstruction, time:", time.time() - time0)
    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6)
    csd_fit = csd_model.fit(data, mask=white_matter)

    csa_model = CsaOdfModel(gtab, sh_order=6)
    gfa = csa_model.fit(data, mask=white_matter).gfa
    stopping_criterion = ThresholdStoppingCriterion(gfa, Threshold)

    print("begin tracking, time:", time.time() - time0)
    fod = csd_fit.odf(small_sphere)
    pmf = fod.clip(min=0)
    prob_dg = ProbabilisticDirectionGetter.from_pmf(pmf, max_angle=30., sphere=small_sphere)
    streamline_generator = LocalTracking(prob_dg, stopping_criterion, seeds, affine, step_size=.5)
    streamlines = Streamlines(streamline_generator)

    sft = StatefulTractogram(streamlines, img, Space.RASMM)

    if one_node or two_node:
        sft.to_vox()
        streamlines = reduct_seed_ROI(sft.streamlines, seed_mask, one_node, two_node)
        sft = StatefulTractogram(streamlines, img, Space.VOX)
        sft._vox_to_rasmm()

    print("begin saving, time:", time.time() - time0)

    output = 'tractogram_probabilistic.trk'
    save_trk(sft, output)

    print("finished, time:", time.time() - time0)

def determine(name=None, data_path=None, output_path='.', Threshold=.20, data_list=None, seed='.'
              , minus_ROI_mask='.', one_node=False, two_node=False):


    time0 = time.time()
    print("begin loading data, time:", time.time() - time0)

    if data_list == None:
        data, affine, img, labels, gtab, head_mask = get_data(name, data_path)
    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        labels = data_list['labels']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']

    print(type(seed))

    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (labels == 2) * (head_mask == 1)

    white_matter =  (labels == 2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    print("begin reconstruction, time:", time.time() - time0)
    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6)
    csd_fit = csd_model.fit(data, mask=white_matter)


    csa_model = CsaOdfModel(gtab, sh_order=6)
    gfa = csa_model.fit(data, mask=white_matter).gfa
    stopping_criterion = ThresholdStoppingCriterion(gfa, Threshold)

    #from dipy.data import small_sphere


    print("begin tracking, time:", time.time() - time0)
    detmax_dg = DeterministicMaximumDirectionGetter.from_shcoeff(
        csd_fit.shm_coeff, max_angle=30., sphere=default_sphere)
    streamline_generator = LocalTracking(detmax_dg, stopping_criterion, seeds,
                                         affine, step_size=.5)
    streamlines = Streamlines(streamline_generator)
    sft = StatefulTractogram(streamlines, img, Space.RASMM)

    if one_node or two_node:
        sft.to_vox()
        streamlines = reduct_seed_ROI(sft.streamlines, seed_mask, one_node, two_node)

        if type(minus_ROI_mask) != str:

            streamlines = minus_ROI(streamlines=streamlines, ROI=minus_ROI_mask)

        sft = StatefulTractogram(streamlines, img, Space.VOX)
        sft._vox_to_rasmm()

    print("begin saving, time:", time.time() - time0)

    output = output_path + '/tractogram_deterministic_' + name + '.trk'
    save_trk(sft, output)

    print("finished, time:", time.time() - time0)

def basic_tracking(name=None, data_path=None, output_path='.', Threshold=.20, data_list=None):



    time0 = time.time()
    print("begin loading data, time:", time.time() - time0)

    if data_list == None:
        data, affine, img, labels, gtab, head_mask = get_data(name, data_path)
    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        labels = data_list['labels']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']

    seed_mask = (labels == 2) * (head_mask == 1)
    white_matter = (labels == 2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    print('begin reconstruction, time:', time.time() - time0)

    from dipy.reconst.csdeconv import auto_response_ssst
    from dipy.reconst.shm import CsaOdfModel
    from dipy.data import default_sphere
    from dipy.direction import peaks_from_model

    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
    csa_model = CsaOdfModel(gtab, sh_order=6)
    csa_peaks = peaks_from_model(csa_model, data, default_sphere,
                                 relative_peak_threshold=.8,
                                 min_separation_angle=45,
                                 mask=white_matter)

    stopping_criterion = ThresholdStoppingCriterion(csa_peaks.gfa, Threshold)


    print("begin tracking, time:", time.time() - time0)
    # Initialization of LocalTracking. The computation happens in the next step.
    streamlines_generator = LocalTracking(csa_peaks, stopping_criterion, seeds,
                                          affine=affine, step_size=.5)
    # Generate streamlines object
    streamlines = Streamlines(streamlines_generator)


    print('begin saving, time:', time.time() - time0)

    from dipy.io.stateful_tractogram import Space, StatefulTractogram
    from dipy.io.streamline import save_trk

    sft = StatefulTractogram(streamlines, img, Space.RASMM)
    output = output_path+'/tractogram_EuDX_'+name+'.trk'
    save_trk(sft, output, streamlines)

def sfm_tracking(name=None, data_path=None, output_path='.', Threshold=.20, data_list=None,
                 return_streamlines=False, save_track=True, seed='.', minus_ROI_mask='.', one_node=False, two_node=False):

    time0 = time.time()
    print("begin loading data, time:", time.time() - time0)

    if data_list == None:
        data, affine, img, labels, gtab, head_mask = get_data(name, data_path)
    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        labels = data_list['labels']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']

    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (labels == 2) * (head_mask == 1)

    white_matter = (labels == 2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    print('begin reconstruction, time:', time.time() - time0)

    from dipy.reconst.csdeconv import auto_response_ssst
    from dipy.reconst.shm import CsaOdfModel
    from dipy.data import default_sphere
    from dipy.direction import peaks_from_model

    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)

    sphere = get_sphere()
    sf_model = sfm.SparseFascicleModel(gtab, sphere=sphere,
                                       l1_ratio=0.5, alpha=0.001,
                                       response=response[0])

    pnm = peaks_from_model(sf_model, data, sphere,
                           relative_peak_threshold=.5,
                           min_separation_angle=25,
                           mask=white_matter,
                           parallel=True)

    stopping_criterion = ThresholdStoppingCriterion(pnm.gfa, Threshold)
    #seeds = utils.seeds_from_mask(white_matter, affine, density=1)

    print('begin tracking, time:', time.time() - time0)

    streamline_generator = LocalTracking(pnm, stopping_criterion, seeds, affine,
                                         step_size=.5)
    streamlines = Streamlines(streamline_generator)



    print('begin saving, time:', time.time() - time0)

    from dipy.io.stateful_tractogram import Space, StatefulTractogram
    from dipy.io.streamline import save_trk

    if save_track:

        sft = StatefulTractogram(streamlines, img, Space.RASMM)

        if one_node or two_node:
            sft.to_vox()
            streamlines = reduct_seed_ROI(sft.streamlines, seed_mask, one_node, two_node)

            if type(minus_ROI_mask) != str:
                streamlines = minus_ROI(streamlines=streamlines, ROI=minus_ROI_mask)

            sft = StatefulTractogram(streamlines, img, Space.VOX)
            sft._vox_to_rasmm()



        output = output_path + '/tractogram_sfm_' + name + '.trk'
        save_trk(sft, output, streamlines)

    if return_streamlines:
        return streamlines

def PFT_tracking(name=None, data_path=None, output_path='.', Threshold=.20):


    time0 = time.time()
    print("begin loading data, time:", time.time() - time0)
    data, affine, img, labels, gtab, head_mask = get_data(name, data_path)

    seed_mask = (labels == 2) * (head_mask == 1)
    white_matter = (labels == 2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    print('begin reconstruction, time:', time.time() - time0)

    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response)
    csd_fit = csd_model.fit(data, mask=white_matter)

    csa_model = CsaOdfModel(gtab, sh_order=6)
    gfa = csa_model.fit(data, mask=white_matter).gfa

    stopping_criterion = ThresholdStoppingCriterion(gfa, Threshold)


    dg = ProbabilisticDirectionGetter.from_shcoeff(csd_fit.shm_coeff,
                                                   max_angle=20.,
                                                   sphere=default_sphere)

    #seed_mask = (labels == 2)
    #seed_mask[pve_wm_data < 0.5] = 0
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)


    #voxel_size = np.average(voxel_size[1:4])
    step_size = 0.2

    #cmc_criterion = CmcStoppingCriterion.from_pve(pve_wm_data,
    #                                              pve_gm_data,
     #                                             pve_csf_data,
     #                                             step_size=step_size,
    #                                              average_voxel_size=voxel_size)

    # Particle Filtering Tractography
    pft_streamline_generator = ParticleFilteringTracking(dg,
                                                         stopping_criterion,
                                                         seeds,
                                                         affine,
                                                         max_cross=1,
                                                         step_size=step_size,
                                                         maxlen=1000,
                                                         pft_back_tracking_dist=2,
                                                         pft_front_tracking_dist=1,
                                                         particle_count=15,
                                                         return_all=False)
    streamlines = Streamlines(pft_streamline_generator)
    sft = StatefulTractogram(streamlines, img, Space.RASMM)
    output = output_path+'/tractogram_pft_'+name+'.trk'

def ClosestPeak(name=None, data_path=None, output_path='.', Threshold=.20):


    time0 = time.time()
    print("begin loading data, time:", time.time() - time0)
    data, affine, img, labels, gtab, head_mask = get_data(name, data_path)

    seed_mask = (labels == 2) * (head_mask == 1)
    white_matter = (labels == 2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    print("begin reconstruction, time:", time.time() - time0)
    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6)
    #csd_fit = csd_model.fit(data, mask=white_matter)
    #pmf = csd_fit.odf(small_sphere).clip(min=0)
    peak_dg = BootDirectionGetter.from_data(data, csd_model, max_angle=30., sphere = small_sphere)

    csa_model = CsaOdfModel(gtab, sh_order=6)
    gfa = csa_model.fit(data, mask=white_matter).gfa
    stopping_criterion = ThresholdStoppingCriterion(gfa, Threshold)

    #from dipy.data import small_sphere


    print("begin tracking, time:", time.time() - time0)
    #detmax_dg = DeterministicMaximumDirectionGetter.from_shcoeff(
    #    csd_fit.shm_coeff, max_angle=30., sphere=default_sphere)
    streamline_generator = LocalTracking(peak_dg, stopping_criterion, seeds,
                                         affine, step_size=.5)
    streamlines = Streamlines(streamline_generator)
    sft = StatefulTractogram(streamlines, img, Space.RASMM)

    print("begin saving, time:", time.time() - time0)

    output = output_path + '/tractogram_ClosestPeak_' + name + '.trk'
    save_trk(sft, output)

    print("finished, time:", time.time() - time0)
