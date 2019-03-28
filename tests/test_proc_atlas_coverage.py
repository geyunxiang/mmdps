"""
This script is used to test the calculation of area mapping in different atlas objects
"""
from mmdps.proc import atlas

def main():
	atlasBase = atlas.get('aicha')
	atlasTarget = atlas.get('brodmann_lr')
	regionTick = 'S_Precentral-1-L'
	atlas.region_overlap_report(regionTick, atlasBase, atlasTarget)

if __name__ == '__main__':
	main()