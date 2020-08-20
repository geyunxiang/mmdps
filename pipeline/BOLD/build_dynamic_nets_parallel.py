"""
This script is used to calculate the dynamic networks
and store them somewhere proper.
"""

import os
import numpy as np
import multiprocessing, queue

from mmdps.proc import atlas, parabase
from mmdps.util.loadsave import load_nii, save_csvmat
from mmdps.util import loadsave

class CalcDynamic:
	def __init__(self, atlasobj, volumename, img, outfolder, windowLength = 100, stepsize = 3):
		"""
		volumename = '3mm' is the name of the atlas volume
		img is the nii file loaded using load_nii function
		"""
		self.img = img
		self.atlasobj = atlasobj
		self.atlasimg = load_nii(atlasobj.get_volume(volumename)['niifile'])
		self.outfolder = outfolder
		self.stepsize = stepsize
		self.windowLength = windowLength

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
		timepoints = ts.shape[1] # number of total timepoints
		start = 0
		while start + self.windowLength < timepoints:
			tscorr = np.corrcoef(ts[:, start:start + self.windowLength])
			save_csvmat(self.outpath('corrcoef-%d-%d.csv' % (start, start + self.windowLength)), tscorr)
			start += self.stepsize

	def run(self):
		self.gen_net()

def func(args):
	subject = args[0]
	atlasname = args[1]
	volumename = '3mm'
	atlasobj = atlas.get(atlasname)
	work_path = 'D:/Research/xuquan_FMRI/Dynamic tfMRI work/'
	outfolder = os.path.join(work_path, subject, atlasname, 'bold_net', 'dynamic_1_10')
	img = load_nii(os.path.join(work_path, subject, 'pBOLD.nii'))
	os.makedirs(outfolder, exist_ok = True)
	c = CalcDynamic(atlasobj, volumename, img, outfolder, 10, 1)
	c.run()

if __name__ == '__main__':
	atlasList = ['brodmann_lrce']
	mriscanstxt = 'D:/Research/xuquan_FMRI/DPARSFA work/namelist.txt'
	subjectList = loadsave.load_txt(mriscanstxt)
	taskList = []
	for subject in subjectList:
		for atlasname in atlasList:
			taskList.append((subject, atlasname))
	taskCount = len(taskList)
	totalResult = []
	pool = multiprocessing.Pool(processes = 4)
	manager = multiprocessing.Manager()
	managerQueue = manager.Queue()
	fwrap = parabase.FWrap(func, managerQueue)
	result = pool.map_async(fwrap.run, taskList)
	nfinished = 0
	while True:
		if result.ready():
			break
		else:
			try:
				res = managerQueue.get(timeout=1)
			except queue.Empty:
				continue
			else:
				nfinished += 1
				print('finished one, %d left' % (taskCount - nfinished))
	print('End proc')
	totalResult.append(result.get())
	pool.close()
	pool.join()
	print(totalResult)
