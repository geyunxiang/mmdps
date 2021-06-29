import os
import numpy as np

from mmdps.util.loadsave import load_nii, save_csvmat,load_json

from mmdps.util import path
from mmdps.proc import atlas

class Calc:
	def __init__(self, atlasobj, volumename, img, outfolder, windowLength = 100, stepSize = 1):
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
			# print(region)
			# print((atlasData==region).shape,data.shape)
			regionDots = data[atlasData==region, start:start+self.windowLength]
			# print(regionDots.shape)
			regionTimeSeries = np.mean(regionDots, axis=0)
			timeseries[i, :] = regionTimeSeries
		# print(data[atlasData==region, :])
		return timeseries

	def gen_net(self):
		# print(self.get_total_time_points())
		for start in range(0, self.get_total_time_points()-self.windowLength+1, self.stepSize):
			ts = self.gen_timeseries(start)
			if ts is None:
				# print(start,)
				raise Exception('Dynamic sliding window exceeds total time points')
			save_csvmat(self.outpath('timeseries-%d-%d.csv' % (start, start+self.windowLength)), ts)
			tscorr = np.corrcoef(ts)
			save_csvmat(self.outpath('corrcoef-%d-%d.csv' % (start, start+self.windowLength)), tscorr)

	def run(self):
		self.gen_net()

if __name__=="__main__":
	atlasobj = path.curatlas()
	volumename = '3mm'
	img = load_nii(os.path.join(path.curparent(), 'pBOLD.nii'))


	json_path = path.fullfile("inter_attr_dynamic.json")
	argsDict = load_json(json_path)	
	outfolder = os.path.join(os.getcwd(),'bold_net','dynamic_'+str(argsDict['stepSize'])+"_"+str(argsDict['windowLength']))
	os.makedirs(outfolder, exist_ok = True)
	# c = Calc(atlasobj, volumename, img, outfolder)
	# c.run()
	# atlasobj, volumename, img, outfolder, windowLength = 100, stepSize = 3
	# print(outfolder)
	# print(volumename)
	cal = Calc(atlasobj = atlasobj, volumename = volumename, img = img, outfolder = outfolder,windowLength=argsDict['windowLength'],stepSize=argsDict['stepSize'])
	cal.run()
