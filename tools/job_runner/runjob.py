"""Run a job."""

import sys, os
import argparse
from mmdps.proc import job
from mmdps.util import loadsave
from mmdps.util import path

def runjob(job, folder=None):
	if folder:
		with job.ChangeDirectory(folder):
			return job.run()
	else:
		return job.run()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', help='job config json file', required=True)
	parser.add_argument('--folder', help='job run in this folder', default=None)
	args = parser.parse_args()
	print(args.folder)
	configfile = path.fullfile(args.config)
	print(configfile)
	configdict = loadsave.load_json(configfile)
	curjob = job.load(configdict)
	runjob(curjob, args.folder)
	sys.stdin.close()
	sys.stdout.close()
	sys.stderr.close()
