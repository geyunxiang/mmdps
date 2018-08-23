"""Parallel can run one job in many different folders in parallel.

Parallel is used to run one job in many folders in parallel.
The folders should be in the same parent folder.
There is a second order parameter. If true, the folders in secondlist
will multiply the folders in folderlist.
If there are m folders in folderlist, the bsecond is True, n folders 
in secondlist, there will be m * n jobs to be run in parallel.

T1
  P00
	aal
	brodmann_lr
  P01
	aal
	brodmann_lr
	
the folder list contains [P00, P01], the secondlist contains [aal, brodmann_lr].
If use bsecond is True, the job will run in the four folders in parallel.
"""

import os
import functools
from collections import OrderedDict

# from . import job, parabase
# from ..util import loadsave
# from ..util import path

from mmdps.proc import job, parabase
from mmdps.util import loadsave, path

class Para:
	def __init__(self, name, mainfolder, jobconfig, folderlist, runmode, bsecond=False, secondlist=''):
		"""Init the Para.

		mainfolder, the parent folder of all folders.
		jobconfig, the job to be run in multiple places.
		folderlist, the folders to run the job in each one.
		runmode, 'Parallel', 'Sequential', 'FirstOnly'.
		bsecond, whether use second order.
		secondlist, the second order folders.
		"""
		self.name = name
		self.mainfolder = mainfolder
		self.jobconfig = jobconfig
		self.folderlist = folderlist
		self.runmode = runmode
		self.bsecond = bsecond
		self.secondlist = secondlist

	@classmethod
	def from_dict(cls, d):
		"""Create the parallel from dict."""
		name = d['name']
		mainfolder = d['MainFolder']
		folderlist = d['FolderList']
		bsecond = d['Second']
		secondlist = d['SecondList']
		jobconfig = d['JobConfig']
		runmode = d['RunMode']
		o = cls(name, mainfolder, jobconfig, folderlist, runmode, bsecond, secondlist)
		return o

	def to_dict(self):
		"""Serialize to dict."""
		d = OrderedDict()
		d['name'] = self.name
		d['MainFolder'] = self.mainfolder
		d['FolderList'] = self.folderlist
		d['Second'] = self.bsecond
		d['SecondList'] = self.secondlist
		d['JobConfig'] = self.jobconfig
		d['RunMode'] = self.runmode
		return d

	def run_seq(self, jobobj, folders):
		"""Run all jobs sequentially."""
		for folder in folders:
			b = job.runjob(jobobj, folder)
			if b != 0:
				return b

	def run_para(self, jobobj, folders):
		"""Run all jobs in parallel."""
		f = functools.partial(job.runjob, jobobj)
		return parabase.run(f, folders)
		#return parabase.run_simple(f, folders)

	def run(self):
		"""Run the para.
		finalfolders is the constructed folder in which to run the job in parallel,
		Or sequential if configured that way.
		Env MMDPS_NEWLIST_TXT will override folderlist.
		Env MMDPS_SECONDLIST_TXT will override secondlist.
		"""
		originalfolders = loadsave.load_txt(path.env_override(self.folderlist, 'MMDPS_NEWLIST_TXT'))
		folders = [os.path.join(self.mainfolder, f) for f in originalfolders]
		if self.bsecond:
			finalfolders = []
			secondfolders = loadsave.load_txt(path.env_override(self.secondlist, 'MMDPS_SECONDLIST_TXT'))
			for folder in folders:
				for secondfolder in secondfolders:
					newfolder = os.path.join(folder, secondfolder)
					path.makedirs(newfolder)
					finalfolders.append(newfolder)
		else:
			finalfolders = folders
		currentJob = job.load(loadsave.load_json(path.fullfile(self.jobconfig)))
		if self.runmode == 'FirstOnly':
			return self.run_seq(currentJob, finalfolders[0:1])
		if self.runmode == 'Parallel':
			return self.run_para(currentJob, finalfolders)
		if self.runmode == 'Sequential':
			return self.run_seq(currentJob, finalfolders)
		else:
			print('Error: no such runmode as', self.runmode)
			return None

def load(d):
	"""Load a Para from dict."""
	para = Para.from_dict(d)
	return para
