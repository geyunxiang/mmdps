import os
import numpy as np
from mmdps.proc import atlas, fusion, netattr
from mmdps.vis import braincircos

def plot_mriscan(fu, mriscan):
    netname = 'bold_net'
    print(mriscan)
    net = fu.nets.load(mriscan, netname)
    netfilepath = fu.nets.loadfilepath(mriscan, netname)
    netfiledir = os.path.dirname(netfilepath)
    atlasobj = fu.atlasobj
    #attr = netattr.Attr(0.5*np.ones(atlasobj.count), atlasobj)
    mean = np.mean(net.data, axis=0)
    attr = netattr.Attr(mean, atlasobj)
    outfilepath = os.path.join(netfiledir, netname + '_circos')
    title = '{}\n{}'.format(mriscan, netname)
    p = braincircos.CircosPlot(net, attr, title, outfilepath)
    p.plot()
    

if __name__ == '__main__':
    atlasobj = atlas.getbyenv('brodmann_lrce')
    fu = fusion.create_by_folder(atlasobj, 'E:/MMDPSoftware/mmdps/pipeline/Fusion')
    mriscans = fu.groups['entire'].mriscans
    mriscan = 'caochangsheng_20161027'
    plot_mriscan(fu, mriscan)
    
