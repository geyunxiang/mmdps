import json
import numpy as np

def load_txt(txt):
	with open(txt) as f:
		return [l.strip() for l in f]

def load_json(jfile):
	with open(jfile, encoding='utf8') as f:
		return json.load(f)

def load_csvmat(matfile):
	return np.loadtxt(matfile, delimiter=',')

def save_csvmat(matfile, mat):
	np.savetxt(matfile, mat, delimiter = ',')
