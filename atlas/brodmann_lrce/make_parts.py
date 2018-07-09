"""
Raw, from wikipedia:
Frontal lobe
  Superolateral 4,6,8,9,10,46,11,47,44,45
  Medial/inferior 4,6,8,9,11,12,10,25
Parietal lobe
  Superolateral 5,7,39,40,43
  Medial/inferior 1,2,3,5,7
Occipital lobe
  Superolateral 18,19
  Medial/inferior 17
Temporal lobe
  Superolateral 41,42,38,22,21
  Medial/inferior 37,27,28,34,35,36,20
Limbic lobe
  25,24,32,33,23,31,26,29,30

Grouped:
Frontal lobe
  4,6,8,9,10,46,11,47,44,45,12,25
Parietal lobe
  5,7,39,40,43,1,2,3
Occipital lobe
  Superolateral 18,19,17
Temporal lobe
  41,42,38,22,21,37,27,28,34,35,36,20
Limbic lobe
  25,24,32,33,23,31,26,29,30

Sorted:
Frontal lobe
  11,47,44,45,46,10,9,8,6,4
Parietal lobe
  3,1,2,5,7,43,40,39
Occipital lobe
  19,18,17
Temporal lobe
  27,34,28,35,36,41,42,22,21,37,20,38,48
Limbic lobe
  25,24,32,23,26,29,30

"""

import json
from mmdps.proc import atlas


def add_prefix(pre, regions):
    res = []
    for region in regions:
        res.append(pre + str(region))
    return res

    

class BrodmannParts:
    def __init__(self):
        self.initparts()
        self.checkparts()
        self.split_leftright()
        
    def initparts(self):
        self.lobes = {}
        self.lobes['frontal'] = [11,47,44,45,46,10,9,8,6,4]
        self.lobes['parietal'] = [3,1,2,5,7,43,40,39]
        self.lobes['occipital'] = [19,18,17]
        self.lobes['temporal'] = [27,34,28,35,36,41,42,22,21,37,20,38,48]
        self.lobes['limbic'] = [25,24,32,23,26,29,30]

    def checkparts(self):
        atlasobj = atlas.get('brodmann_lr')
        print(atlasobj.regions)
        loberegions = []
        for lobename in self.lobes:
            loberegions.extend(self.lobes[lobename])
        loberegions.sort()
        print(loberegions)
        print(len(loberegions))

    
    def split_leftright(self):
        lobenames = ['frontal', 'parietal', 'temporal', 'occipital', 'limbic']
        for lobename in lobenames:
            print(lobename)
            regions = self.lobes[lobename]
            print(json.dumps(add_prefix('L', regions)))
            print(json.dumps(add_prefix('R', regions)))
            print()

def main():
    BrodmannParts()
    
if __name__ == '__main__':
    main()
    
