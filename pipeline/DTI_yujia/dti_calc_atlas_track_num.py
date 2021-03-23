from pipeline.DTI_yujia.tracking_plus.ROI import ROI_atlas, ROI_atlas_dipy
from mmdps.proc import atlas
from mmdps.util import loadsave

def yujia_method():
	atlasobj = atlas.getbywd()
	track_path = 'tractogram_probabilistic.trk'
	roi_feature = ROI_atlas(atlasobj, track_path = track_path)
	loadsave.save_csvmat('tract_count_yujia.csv', roi_feature)

def dipy_method():
	atlasobj = atlas.getbywd()
	track_path = '../tractogram_probabilistic.trk'
	roi_feature = ROI_atlas_dipy(atlasobj, track_path)
	loadsave.save_csvmat('tract_count.csv', roi_feature)

if __name__ == '__main__':
	dipy_method()
