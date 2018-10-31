import os
import functools
import numpy as np
from mmdps.proc import fusion, atlas, netattr
from mmdps.vis import report, braincircos
from mmdps.util import path, clock
from mmdps.proc import parabase

class BOLDNetCircosPlot(braincircos.CircosPlotBuilder):
    def get_title(self):
        return self.title + '\n' + 'abs(v) > 0.5'
    
class DWINetCircosPlot(braincircos.CircosPlotBuilder):
    def get_title(self):
        return self.title + '\n' + 'v > 2'

class WeakCircosLink(braincircos.CircosLink):
    def get_mask(self):
        mask = np.zeros(self.net.data.shape, dtype=bool)
        threshold = self.threshold
        mask[np.abs(self.net.data) < threshold] = True
        mask[self.net.data == 0] = False
        mask = np.triu(mask, 1)
        return mask
    
class WeakBOLDNetCircosPlot(braincircos.CircosPlotBuilder):
    def get_title(self):
        return self.title + '\n' + 'abs(v) < 0.5'
    
class WeakDWINetCircosPlot(braincircos.CircosPlotBuilder):
    def get_title(self):
        return self.title + '\n' + 'v < 2'

def plot_mriscan(fu, mriscan, netname):
    print(mriscan)
    net = fu.nets.load(mriscan, netname)
    netfilepath = fu.nets.loadfilepath(mriscan, netname)
    netfiledir = os.path.dirname(netfilepath)
    atlasobj = fu.atlasobj
    attrdata = np.mean(net.data, axis=0)
    attr = netattr.Attr(attrdata, atlasobj)
    outfilepath = os.path.join(netfiledir, netname + '_circos')
    title = '{}\n{}\n'.format(mriscan, netname)
    if netname == 'bold_net':
        p = BOLDNetCircosPlot(atlasobj, title, outfilepath)
        p.add_circosvalue(braincircos.CircosValue(attr, (-1, 1)))
        p.add_circoslink(braincircos.CircosLink(net, 0.5, (-1, 1)))
    elif netname == 'dwi_net':
        p = DWINetCircosPlot(atlasobj, title, outfilepath)
        p.add_circosvalue(braincircos.CircosValue(attr, (-100, 100)))
        p.add_circosvalue(braincircos.CircosValue(fu.attrs.load(mriscan, 'dwi_MD'), (-0.003, 0.003)))
        p.add_circosvalue(braincircos.CircosValue(fu.attrs.load(mriscan, 'dwi_FA'), (-1, 1)))
        p.add_circoslink(braincircos.CircosLink(net, 2, (-6, 6)))
    else:
        return
    p.plot()

def plot_mriscan_weak(fu, mriscan, netname):
    print(mriscan)
    net = fu.nets.load(mriscan, netname)
    netfilepath = fu.nets.loadfilepath(mriscan, netname)
    netfiledir = os.path.dirname(netfilepath)
    atlasobj = fu.atlasobj
    attrdata = np.mean(net.data, axis=0)
    attr = netattr.Attr(attrdata, atlasobj)
    outfilepath = os.path.join(netfiledir, netname + '_circos_weak')
    title = '{}\n{}\n'.format(mriscan, netname)
    if netname == 'bold_net':
        p = WeakBOLDNetCircosPlot(atlasobj, title, outfilepath)
        p.add_circosvalue(braincircos.CircosValue(attr, (-1, 1)))
        p.add_circoslink(WeakCircosLink(net, 0.5, (-1, 1)))
    elif netname == 'dwi_net':
        p = WeakDWINetCircosPlot(atlasobj, title, outfilepath)
        p.add_circosvalue(braincircos.CircosValue(attr, (-100, 100)))
        p.add_circosvalue(braincircos.CircosValue(fu.attrs.load(mriscan, 'dwi_MD'), (-0.003, 0.003)))
        p.add_circosvalue(braincircos.CircosValue(fu.attrs.load(mriscan, 'dwi_FA'), (-1, 1)))
        p.add_circoslink(WeakCircosLink(net, 2, (-6, 6)))
    else:
        return
    p.plot()
    
class MRIScanPlotCircos(fusion.ForeachMRIScan):
    def __init__(self, fu, mriscans):
        super().__init__(fu, mriscans)

    def work_net(self, mriscan):
        netnames = fu.nets.names()
        funcs = []
        for netname in netnames:
            try:
                net = fu.nets.load(mriscan, netname)
            except:
                continue
            f = functools.partial(plot_mriscan, fu, mriscan, netname)
            funcs.append(f)
            f2 = functools.partial(plot_mriscan_weak, fu, mriscan, netname)
            funcs.append(f2)
        return funcs
        
    def work(self, mriscan):
        print('--', mriscan)
        rets = []
##        ret = self.work_attr(mriscan)
##        rets.extend(ret)
        ret = self.work_net(mriscan)
        rets.extend(ret)
        return rets
        
def flattenlist(ll):
    ls = []
    for l in ll:
        ls.extend(l)
    return ls

if __name__ == '__main__':
    atlasobj = atlas.getbyenv('brodmann_lrce')
    atlasobj.set_brainparts('alt')
    fu = fusion.create_by_folder(atlasobj, 'E:/MMDPSoftware/mmdps/pipeline/Fusion')
    mriscans = fu.groups['entire'].mriscans
    foreach_scan = MRIScanPlotCircos(fu, mriscans)
    funcslist = foreach_scan.run()
    funcs = flattenlist(funcslist)
    print(len(funcs))
    print(clock.now())
    parabase.run_callfunc(funcs)
##    for func in funcs:
##        func()

    print(clock.now())
        
    
