"""Run a Para."""

import sys
import argparse
from mmdps.proc import para
from mmdps.util.loadsave import load_json
from mmdps.util import path

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', help='para config json file', required=True)
	args = parser.parse_args()
	configpath = path.fullfile(args.config)
	print('Runpara: configpath', configpath)
	configDict = load_json(configpath)
	currentPara = para.load(configDict)
	currentPara.run()
	sys.stdin.close()
	sys.stdout.close()
	sys.stderr.close()
