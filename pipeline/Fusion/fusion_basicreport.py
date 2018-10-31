import os
import numpy as np
from mmdps.proc import fusion, atlas
from mmdps.vis import report
from mmdps.util import path, clock
from mmdps.proc import parabase


class MRIScanReport(fusion.ForeachMRIScan):
    def __init__(self, fu, mriscans):
        super().__init__(fu, mriscans)

    def work_attr(self, mriscan):
        attrnames = fu.attrs.names()
        funcs = []
        for attrname in attrnames:
            try:
                attr = fu.attrs.load(mriscan, attrname)
            except FileNotFoundError:
                continue
            attrfile = fu.attrs.loadfilepath(mriscan, attrname)
            attrfilename = os.path.basename(attrfile)
            attrdir = os.path.dirname(attrfile)
            filenoext, ext = path.splitext(attrfilename)
            outwithtick = os.path.join(attrdir, filenoext + '_withtick' + ext)
            print(outwithtick)
            attr.save(outwithtick)
            name, ext = path.splitext(attrfile)
            rpt = report.PlotAttr(attrname, attr, mriscan + '_' + attrname, name + '.png')
            #rpt.run()
            funcs.append(rpt.run)
        return funcs

    def work_net(self, mriscan):
        netnames = fu.nets.names()
        funcs = []
        for netname in netnames:
            try:
                net = fu.nets.load(mriscan, netname)
            except:
                continue
            netfile = fu.nets.loadfilepath(mriscan, netname)
            netfilename = os.path.basename(netfile)
            netfiledir = os.path.dirname(netfile)
            filenoext, ext = path.splitext(netfilename)
            outwithtick = os.path.join(netfiledir, filenoext + '_withtick' + ext)
            print(outwithtick)
            net.save(outwithtick)
            name, ext = path.splitext(netfile)
            rpt = report.PlotNet(netname, net, mriscan + '_' + netname, name + '.png')
            funcs.append(rpt.run)
        return funcs
    
    def work(self, mriscan):
        print('--', mriscan)
        rets = []
        ret = self.work_attr(mriscan)
        rets.extend(ret)
        #ret = self.work_net(mriscan)
        #rets.extend(ret)
        return rets
        
def flattenlist(ll):
    ls = []
    for l in ll:
        ls.extend(l)
    return ls

if __name__ == '__main__':
    atlasobj = atlas.getbyenv('aal')
    fu = fusion.create_by_folder(atlasobj, 'E:/MMDPSoftware/mmdps/pipeline/Fusion')
    mriscans = fu.groups['entire'].mriscans
    foreach_scan = MRIScanReport(fu, mriscans)
    funcslist = foreach_scan.run()
    funcs = flattenlist(funcslist)
    print(len(funcs))
    print(clock.now())
    parabase.run_callfunc(funcs)
##    for func in funcs:
##        func()

    print(clock.now())
        
    
