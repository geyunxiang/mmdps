import os
from mmdps.util import dwi
from dipy.tracking import utils
import nibabel as nib
from dipy.io import pickles

class Struct:
    pass

def track_gen_net_work(tracks, img_template):
    labels = img_template.get_data()
    labels = labels.astype(int)
    M, grouping = utils.connectivity_matrix(tracks, labels, affine=img_template.get_affine(),
                              return_mapping=True, mapping_as_streamlines=True)
    p = Struct()
    p.M = M
    p.grouping = grouping
    return p

def track_gen_net(trackpickle, templatepath):
    tracks = dwi.load_streamlines_from_trk(trackpickle)
    img_template = nib.load(templatepath)
    p = track_gen_net_work(tracks, img_template)
    pickles.save_pickle('net_gen_net.pickle', p)

if __name__ == '__main__':
    spacename = os.path.basename(os.getcwd())
    trackfile = os.path.join('../../', spacename, 'raw_track.trk')
    templatepath = 'wtemplate_2.nii.gz'
    track_gen_net(trackfile, templatepath)
