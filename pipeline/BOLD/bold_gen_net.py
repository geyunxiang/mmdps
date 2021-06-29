import os
import numpy as np
import nibabel as nib

from mmdps.proc import atlas
from mmdps.util.loadsave import load_nii, save_csvmat
from mmdps.util import path

class Calc:
	def __init__(self, atlasobj, volumename, img, outfolder):
		self.img = img
		self.atlasobj = atlasobj
		self.atlasimg = load_nii(atlasobj.get_volume(volumename)['niifile'])
		self.outfolder = outfolder

	def outpath(self, *p):
		return os.path.join(self.outfolder, *p)

	def gen_timeseries(self):
		data = self.img.get_data()
		atdata = self.atlasimg.get_data()
		timepoints = data.shape[3]
		timeseries = np.empty((self.atlasobj.count, timepoints))
		for i, region in enumerate(self.atlasobj.regions):
			regiondots = data[atdata==region, :]
			regionts = np.mean(regiondots, axis=0)
			timeseries[i, :] = regionts
		return timeseries

	def gen_net(self):
		ts = self.gen_timeseries()
		save_csvmat(self.outpath('timeseries.csv'), ts)
		tscorr = np.corrcoef(ts)
		save_csvmat(self.outpath('corrcoef.csv'), tscorr)

	def run(self):
		self.gen_net()

if __name__ == '__main__':
	atlasobj = path.curatlas()
	volumename = '3mm'
	img = load_nii(os.path.join(path.curparent(), 'pBOLD.nii'))
	outfolder = 'bold_net'

	c = Calc(atlasobj, volumename, img, outfolder)
	c.run()
