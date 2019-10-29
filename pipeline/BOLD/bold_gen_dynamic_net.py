import os
import numpy as np

from mmdps.util.loadsave import load_nii, save_csvmat

class Calc:
	def __init__(self, atlasobj, volumename, img, outfolder, windowLength = 100, stepSize = 3):
		self.img = img
		self.atlasobj = atlasobj
		self.atlasimg = load_nii(atlasobj.get_volume(volumename)['niifile'])
		self.outfolder = outfolder
		self.windowLength = windowLength
		self.stepSize = stepSize

	def outpath(self, *p):
		return os.path.join(self.outfolder, *p)

	def get_total_time_points(self):
		data = self.img.get_data()
		return data.shape[3]

	def gen_timeseries(self, start):
		data = self.img.get_data()
		atlasData = self.atlasimg.get_data()
		timepoints = data.shape[3]
		if start + self.windowLength > timepoints:
			return None
		timeseries = np.empty((self.atlasobj.count, self.windowLength))
		for i, region in enumerate(self.atlasobj.regions):
			regionDots = data[atlasData==region, start:start+self.windowLength]
			regionTimeSeries = np.mean(regionDots, axis=0)
			timeseries[i, :] = regionTimeSeries
		return timeseries

	def gen_net(self):
		for start in range(0, self.get_total_time_points(), self.stepSize):
			ts = self.gen_timeseries(start)
			if ts is None:
				raise Exception('Dynamic sliding window exceeds total time points')
			save_csvmat(self.outpath('timeseries-%d-%d.csv' % (start, self.stepSize)), ts)
			tscorr = np.corrcoef(ts)
			save_csvmat(self.outpath('corrcoef-%d-%d.csv' % (start, self.stepSize)), tscorr)

	def run(self):
		self.gen_net()
