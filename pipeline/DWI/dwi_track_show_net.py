
import pickle
from dipy.io import pickles
import numpy as np
from mmdps.proc import atlas
from mmdps.util.loadsave import save_csvmat
import os

class Struct:
    pass

def gen_net_csv():
    netpickle = 'net_gen_net.pickle'
    net = pickles.load_pickle(netpickle)
    M = net.M
    atlasdir = os.path.dirname(os.getcwd())
    atlasname = os.path.basename(atlasdir)
    atlasobj = atlas.get(atlasname)
    idx = atlasobj.regions
    realM = M[idx][:,idx]
    save_csvmat('dwinetraw.csv', realM)
    save_csvmat('dwinet.csv', np.log1p(realM))
    return realM

if __name__ == '__main__':
    realM = gen_net_csv()
