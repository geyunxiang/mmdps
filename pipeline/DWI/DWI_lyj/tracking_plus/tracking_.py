from dipy.core.gradients import gradient_table
from dipy.data import get_fnames
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti, load_nifti_data, save_nifti
from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel,
                                   auto_response_ssst)
from dipy.tracking import utils
from dipy.tracking.local_tracking import LocalTracking, ParticleFilteringTracking
from dipy.tracking.streamline import Streamlines
from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion, CmcStoppingCriterion

from dipy.io.stateful_tractogram import Space, StatefulTractogram
from dipy.io.streamline import save_trk
from dipy.data import small_sphere, default_sphere, get_sphere
from dipy.reconst.shm import CsaOdfModel
from dipy.reconst import sfm
from dipy.direction import ProbabilisticDirectionGetter, DeterministicMaximumDirectionGetter, ClosestPeakDirectionGetter, BootDirectionGetter
import numpy as np

from tracking_plus.utils import get_data
from tracking_plus import sfm_, peaks_
from tracking_plus.eval_ import get_evals_map


#5 tracking methods


def probal(name=None, data_path=None, output_path='.',
           norm='normalized_pDWI.nii.gz', bvec='DWI.bvec', bval='DWI.bval',
           mask='normalized_mask.nii.gz', FA='FA.nii.gz',
           Threshold=.2, data_list=None, seed='.'):


    if data_list == None:
        data, affine, img, gtab, head_mask, FA = get_data(data_path=data_path,
                                                          norm=norm, bval=bval, bvec=bvec,
                                                          mask=mask, FA=FA)
    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']
        FA = data_list['FA']

    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (FA > Threshold) * (head_mask == 1)


    white_matter = (FA > 0.2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6)
    csd_fit = csd_model.fit(data, mask=white_matter)

    csa_model = CsaOdfModel(gtab, sh_order=6)
    gfa = csa_model.fit(data, mask=white_matter).gfa
    stopping_criterion = ThresholdStoppingCriterion(gfa, Threshold)

    print("begin tracking, time:", time.time() - time0)
    fod = csd_fit.odf(small_sphere)
    pmf = fod.clip(min=0)
    prob_dg = ProbabilisticDirectionGetter.from_pmf(pmf, max_angle=30.,
                                                    sphere=small_sphere)
    streamline_generator = LocalTracking(prob_dg, stopping_criterion, seeds,
                                         affine, step_size=.5)
    streamlines = Streamlines(streamline_generator)

    sft = StatefulTractogram(streamlines, img, Space.RASMM)

    output = output_path+'/tractogram_probabilistic_'+name+'.trk'

    save_trk(sft, output)



def determine(name=None, data_path=None, output_path='.',
            norm='normalized_pDWI.nii.gz', bvec='DWI.bvec', bval='DWI.bval',
            mask='normalized_mask.nii.gz', FA='FA.nii.gz',
            Threshold=.2, data_list=None, seed='.'):



    if data_list == None:
        data, affine, img, gtab, head_mask, FA = get_data(data_path=data_path,
                                                              norm=norm, bval=bval, bvec=bvec,
                                                              mask=mask, FA=FA)
    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']
        FA = data_list['FA']


    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (FA>Threshold) * (head_mask == 1)

    white_matter =  (FA > 0.2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6)
    csd_fit = csd_model.fit(data, mask=white_matter)


    csa_model = CsaOdfModel(gtab, sh_order=6)
    gfa = csa_model.fit(data, mask=white_matter).gfa
    stopping_criterion = ThresholdStoppingCriterion(gfa, Threshold)


    detmax_dg = DeterministicMaximumDirectionGetter.from_shcoeff(
        csd_fit.shm_coeff, max_angle=30., sphere=default_sphere)
    streamline_generator = LocalTracking(detmax_dg, stopping_criterion, seeds,
                                         affine, step_size=.5)
    streamlines = Streamlines(streamline_generator)
    sft = StatefulTractogram(streamlines, img, Space.RASMM)

    output = output_path + '/tractogram_deterministic_' + name + '.trk'
    save_trk(sft, output)


def basic_tracking(name=None, data_path=None,
                   norm='normalized_pDWI', bval='DWI.bval', bvec='DWI.bvec',
                   FA='FA.nii.gz', mask='normalized_mask',
                   output_path='.', Threshold=.20, data_list=None, seed='.'):


    if data_list == None:
        data, affine, img, gtab, head_mask, FA = get_data(data_path=data_path,
                                                          norm=norm, bval=bval, bvec=bvec,
                                                          mask=mask, FA=FA)
    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']
        FA = data_list['FA']



    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (FA>Threshold) * (head_mask == 1)

    white_matter =  (FA > 0.2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)


    from dipy.reconst.csdeconv import auto_response_ssst
    from dipy.reconst.shm import CsaOdfModel
    from dipy.data import default_sphere
    from dipy.direction import peaks_from_model

    csa_model = CsaOdfModel(gtab, sh_order=6)
    csa_peaks = peaks_from_model(csa_model, data, default_sphere,
                                 relative_peak_threshold=.8,
                                 min_separation_angle=45,
                                 mask=seed_mask)

    stopping_criterion = ThresholdStoppingCriterion(csa_peaks.gfa, Threshold)


    streamlines_generator = LocalTracking(csa_peaks, stopping_criterion, seeds,
                                          affine=affine, step_size=.5)
    # Generate streamlines object
    streamlines = Streamlines(streamlines_generator)

    from dipy.io.stateful_tractogram import Space, StatefulTractogram
    from dipy.io.streamline import save_trk

    sft = StatefulTractogram(streamlines, img, Space.RASMM)
    output = output_path+'/tractogram_EuDX_'+name+'.trk'
    save_trk(sft, output, streamlines)

def sfm_tracking(name=None, data_path=None,
                 norm='normalized_pDWI', bval='DWI.bval', bvec='DWI.bvec',
                 FA='FA.nii.gz', mask='normalized_mask',
                 output_path='.', Threshold=.20, data_list=None, seed='.'):

    if data_list == None:
        data, affine, img, gtab, head_mask, FA = get_data(data_path=data_path,
                                                              norm=norm, bval=bval, bvec=bvec,
                                                              mask=mask, FA=FA)
    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']
        FA = data_list['FA']

    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (FA>Threshold) * (head_mask == 1)

    white_matter =  (FA > 0.2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

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


    streamline_generator = LocalTracking(pnm, stopping_criterion, seeds, affine,
                                         step_size=.5)
    streamlines = Streamlines(streamline_generator)

    from dipy.io.stateful_tractogram import Space, StatefulTractogram
    from dipy.io.streamline import save_trk

    sft = StatefulTractogram(streamlines, img, Space.RASMM)
    output = output_path + '/tractogram_sfm_' + name + '.trk'
    save_trk(sft, output, streamlines)


def sfm_new(name=None, data_path=None,
                 norm='normalized_pDWI', bval='DWI.bval', bvec='DWI.bvec',
                 FA='FA.nii.gz', mask='normalized_mask',
                 output_path='.', Threshold=.20, data_list=None, seed='.',
                 evals_map=None, index_map=None):



    if data_list == None:
        data, affine, img, gtab, head_mask, FA = get_data(data_path=data_path,
                                                          norm=norm, bval=bval, bvec=bvec,
                                                          mask=mask, FA=FA)
    if evals_map == None or index_map == None:
        evals_map, index_map = get_evals_map(gtab, data, head_mask, FA)
        save_nifti(data_path + '/' + 'evals_map.nii.gz', evals_map, affine)
        save_nifti(data_path + '/' + 'index_map.nii.gz', index_map, affine)

    else:
        data = data_list['DWI']
        affine = data_list['affine']
        img = data_list['img']
        gtab = data_list['gtab']
        head_mask = data_list['head_mask']
        FA = data_list['FA']

    if type(seed) != str:
        seed_mask = seed
    else:
        seed_mask = (FA > Threshold) * (head_mask == 1)

    white_matter = (FA > 0.2) * (head_mask == 1)
    seeds = utils.seeds_from_mask(seed_mask, affine, density=1)

    from dipy.reconst.csdeconv import auto_response_ssst
    from dipy.reconst.shm import CsaOdfModel
    from dipy.data import default_sphere
    from dipy.direction import peaks_from_model_

    sphere = get_sphere()
    sf_model = sfm_.SparseFascicleModel(gtab, sphere=sphere,
                                        l1_ratio=0.5, alpha=0.001,
                                        evals_map=evals_map,
                                        index_map=index_map)

    pnm = peaks_.peaks_from_model(sf_model, data, sphere,
                           relative_peak_threshold=.5,
                           min_separation_angle=25,
                           mask=white_matter,
                           parallel=False)

    stopping_criterion = ThresholdStoppingCriterion(pnm.gfa, Threshold)

    streamline_generator = LocalTracking(pnm, stopping_criterion, seeds, affine,
                                         step_size=.5)

    streamlines = Streamlines(streamline_generator)
    sft = StatefulTractogram(streamlines, img, Space.RASMM)
    output = output_path + '/tractogram_sfmnew_' + name + '.trk'
    save_trk(sft, output, streamlines)


