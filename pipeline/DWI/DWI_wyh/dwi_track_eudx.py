from dipy.reconst.dti import TensorModel, quantize_evecs

from dipy.data import get_sphere

from dipy.tracking.eudx import EuDX

from dipy.io import pickles

from mmdps.util import dwi

class Struct:
    pass


def track_eudx_work(trackmodel):
    ten = trackmodel.ten
    ind = trackmodel.ind
    sphere = trackmodel.sphere
    eu = EuDX(a=ten.fa, ind=ind, seeds=10**5*5, odf_vertices=sphere.vertices, a_low=0.2)
    tracks = [e for e in eu]
    return tracks

def track_eudx(trackmodelpickle):
    trackmodel = pickles.load_pickle(trackmodelpickle)
    tracks = track_eudx_work(trackmodel)
    with open('raw_track.trk', 'wb') as ftrkout:
        dwi.save_streamlines_to_trk(tracks, trackmodel.affine, ftrkout)
    

if __name__ == '__main__':
    track_eudx('track_gen_model.pickle')
    

