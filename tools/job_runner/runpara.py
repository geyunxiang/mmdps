"""Run a Para."""

import sys, os
import argparse
from mmdps import proc
import mmdps.proc.para
from mmdps.util.loadsave import load_json
from mmdps.util import path

def runpara(para):
	return para.run()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', help='para config json file', required=True)
	args = parser.parse_args()
	configpath = path.fullfile(args.config)
	print('Runpara: configpath', configpath)
	configDict = load_json(configpath)
	currentPara = proc.para.load(configDict)
	runpara(currentPara)
	sys.stdin.close()
	sys.stdout.close()
	sys.stderr.close()
