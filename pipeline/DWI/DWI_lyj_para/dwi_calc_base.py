import json
from mmdps.util import path

class dwi_calc_base(object):
    def __init__(self):
        self._basicConfigName = 'basic_config.json'
        self._basicConfigKey = ['norm_DWI_name','brain_mask_name','bval_name','bvec_name']
        self.argsDict = {}
        self.fromjson(self.name2path(self._basicConfigName),self._basicConfigKey)
    
    def fromjson(self,path:str,restrict:list):
        with open(path, 'r') as fileR:  # open config file
            strF = fileR.read()
            if len(strF) == 0:
                raise Exception('Empty file Error: '+path)
            else:
                R = json.loads(strF)
                for k in restrict:
                    if k not in R.keys():
                        raise Exception('Misssing Required args: '+k+ ', in '+path)
                self.argsDict.update(R)

    def calc(self):
        '''start calculate'''   
        pass

    
    def name2path(self,name):
        _tmp = path.fullfile(name)
        assert _tmp, name+' not found in search path'
        return _tmp

        