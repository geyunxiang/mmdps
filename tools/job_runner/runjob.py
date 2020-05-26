"""Run a job."""

import sys, os
import argparse
from mmdps.proc import job
from mmdps.util import loadsave
from mmdps.util import path

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', help='job config json file', required=True)
	parser.add_argument('--folder', help='job run in this folder', default=None)
	args = parser.parse_args()
	print('Runjob Folder:', args.folder)
	configfile = path.fullfile(args.config)
	print('Runjob File:', configfile)
	configdict = loadsave.load_json(configfile)
	currentJob = job.create_from_dict(configdict)
	job.runjob(currentJob, args.folder)
	sys.stdin.close()
	sys.stdout.close()
	sys.stderr.close()
