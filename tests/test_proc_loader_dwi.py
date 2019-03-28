"""
This script is used to test loading dwi attributes
"""
from mmdps.proc import atlas, loader
import mmdps_locale

def main():
	atlasobj = atlas.get('brodmann_lr')
	dwiLoader = loader.AttrLoader(mmdps_locale.ChanggungFeatureRoot, atlasobj)
	dwiFA = dwiLoader.loadvstackmulti(['chenyifan_20150612', 'chenyifan_20150923'], ['DWI.MD'])
	print(len(dwiFA))
	print(dwiFA.shape)

if __name__ == '__main__':
	main()
