"""
This script is used to test loading dwi attributes
"""
import numpy as np
from mmdps.proc import atlas, loader

atlasobj = atlas.get('brodmann_lrce')

def test_dynamic_network_loader():
	dNet = loader.load_single_dynamic_network('CMSA_01', atlasobj, (100, 3), '/Users/andy/workshop/MSADynamic/')
	dNet_classic = loader.load_dynamic_networks(['CMSA_01'], atlasobj, (100, 3), '/Users/andy/workshop/MSADynamic/')
	print(dNet.data.shape)
	print(len(dNet_classic['CMSA_01']))
	# check
	err_mat = dNet.data[20, :, :] - dNet_classic['CMSA_01'][20].data
	err = np.max(err_mat)
	print(err)

def main():
	pass
	# dwiLoader = loader.AttrLoader(mmdps_locale.ChanggungFeatureRoot, atlasobj)
	# dwiFA = dwiLoader.loadvstackmulti(['chenyifan_20150612', 'chenyifan_20150923'], ['DWI.MD'])
	# print(len(dwiFA))
	# print(dwiFA.shape)

if __name__ == '__main__':
	test_dynamic_network_loader()
