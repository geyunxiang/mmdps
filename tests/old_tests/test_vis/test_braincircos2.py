import os
import numpy as np
from mmdps.proc import atlas, fusion, netattr
from mmdps.vis import braincircos

def plot_mriscan(fu, mriscan):
    netname = 'bold_net'
    title = 'TestCircos'
    outfilepath = 'boldnet'
    atlasobj = fu.atlasobj
    net = fu.nets.load(mriscan, netname)
    attr = fu.attrs.load(mriscan, 'bold_interWD')
    builder = braincircos.CircosPlotBuilder(atlasobj, title, outfilepath)
    builder.add_circosvalue(braincircos.CircosValue(attr))
    builder.add_circosvalue(braincircos.CircosValue(attr, (0, 50)))
    builder.add_circosvalue(braincircos.CircosValue(attr, (0, 100)))
    builder.add_circoslink(braincircos.CircosLink(net))
    builder.plot()

if __name__ == '__main__':
    atlasobj = atlas.getbyenv('brodmann_lrce')
    fu = fusion.create_by_folder(atlasobj, 'E:/MMDPSoftware/mmdps/pipeline/Fusion')
    mriscans = fu.groups['entire'].mriscans
    mriscan = 'caochangsheng_20161027'
    plot_mriscan(fu, mriscan)
    
