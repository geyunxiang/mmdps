from dipy.io import pickles
from mmdps.util import dwi

class Struct:
    pass

def track_eudx_work_old(trackmodel):
    from dipy.tracking.eudx import EuDX
    ten = trackmodel.ten
    ind = trackmodel.ind
    sphere = trackmodel.sphere
    eu = EuDX(a=ten.fa, ind=ind, seeds=10**5*5, odf_vertices=sphere.vertices, a_low=0.2)
    tracks = [e for e in eu]
    return tracks

def track_eudx_old(trackmodelpickle):
    trackmodel = pickles.load_pickle(trackmodelpickle)
    tracks = track_eudx_work_old(trackmodel)
    with open('raw_track.trk', 'wb') as ftrkout:
        dwi.save_streamlines_to_trk(tracks, trackmodel.affine, ftrkout)

def gen_streamline(trackmodelpickle):
    # p = Struct()
    # p.affine = affine
    # p.sphere = sphere
    # p.ten = ten
    # p.ind = ind
    from dipy.tracking.local_tracking import LocalTracking
    from dipy.tracking.streamline import Streamlines
    trackmodel = pickles.load_pickle(trackmodelpickle)
    # see https://dipy.org/documentation/1.1.1./examples_built/tracking_introduction_eudx/#example-tracking-introduction-eudx
    # also see https://dipy.org/documentation/1.1.1./examples_built/reconst_dti/#example-reconst-dti
    pass

if __name__ == '__main__':
    track_eudx_old('track_gen_model.pickle')
