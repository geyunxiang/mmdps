import igraph
import csv
import os
import colorsys
import random
import numpy as np
from mmdps.util import path
from mmdps.proc.atlas import color_atlas_region
from mmdps.vis import bnv
from mmdps.proc import job

def load_txt(txtfile):
    """Load txt list file, line by line."""
    with open(txtfile, 'r') as f:
        return [l.strip() for l in f if l.strip()]


def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step
 
    return hls_colors
 
def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [x for x in (_r, _g, _b)]
        rgb_colors.append((r, g, b, 1.0))
 
    return rgb_colors




def function(net_path,outPath):
    edges,vertex = [], []
    i = 0
    size = 0
    netthreshold = 0.4
    with open(net_path,'r') as f:
        for row in csv.reader(f.read().splitlines()):
            size = len(row)
            ifHasEdge = False
            for j in range(0,len(row)):
                if abs(float(row[j]))>netthreshold and j!=i:
                    if j>i:
                        edges.append((i,j))
                    ifHasEdge = True
            if not ifHasEdge:
                print(i)
                vertex.append(i)
            i = i+1
    
    g = igraph.Graph.TupleList(edges, directed=False, vertex_name_attr='name', edge_attrs=['weight'], weights=False)
    g.add_vertices(vertex)
    # print(vertex)
    size = len(g.vs)
    # print(size)
    # louvain_community = g.community_multilevel()
    # member = louvain_community.membership
    # community_size = louvain_community._len

    walktrap_community = g.community_walktrap().as_clustering()
    member = walktrap_community.membership
    community_size = walktrap_community._len
    # print(edges)
    # print(sorted(g.vs['name']))
    # print(member,len(member))


    color = ncolors(community_size) 
    # color_list =['red','blue','green','cyan','pink','orange','grey','yellow','white','black','purple' ]
    visual_style = {}
    # visual_style["vertex_size"] = g.betweenness()
    # print(g.vs["name"])
    visual_style["vertex_color"] = [color[member[i]] for i in range(size)]
    # print(visual_style['vertex_color'])
    visual_style["vertex_label"] = g.vs["name"]  




    
    bc = {}
    temp = g.betweenness()
    temp_np = np.array(temp)
    temp_np = (temp_np-temp_np.min())/(temp_np.max()-temp_np.min())*20+15
    visual_style['vertex_size'] = temp_np
    for i in range(size):
        if member[i] not in bc.keys():
            bc[member[i]] = {}
        bc[member[i]][i] = temp[i]
    # print(bc)

    for v in bc.values():
        visual_style['vertex_color'][max(v,key=lambda s:v[s])] = 'white'
    # visual_style['layout'] = g.layout('kk')
    # visual_style['layout'] = g.layout('kamada_kawai')
    # igraph.plot(louvain_community,**visual_style).save(os.path.join(outPath,'community_hub_{}.jpg'.format(netthreshold)))

    igraph.plot(walktrap_community,**visual_style).save(os.path.join(outPath,'community_hub_walktrap_{}.jpg'.format(netthreshold)))


    # igraph.plot(louvain_community)
    # print(g)
    # for p in g.vs:
    #     print(p["name"],p.degree())
    # names = g.vs["name"]
    # print(names)
    
    
    # temp1 = sorted(bc,key=lambda k:k['bc'],reverse=True)[0:10]
    # visual_style = {}
    # visual_style['vertex_size'] = g.betweenness()
    # igraph.plot(louvain_community,kwds=visual_style)
    # igraph.plot(g,kwds=visual_style)

    # print(louvain_community.membership)
    # level = [{},{}]
    # with open(community_path,'r') as f:
    #     ifend = -1
    #     for row in csv.reader(f.read().splitlines()):
    #         if int(row[0])==0:
    #             if  ifend==1:
    #                 break
    #             else:
    #                 ifend = ifend+1
    #         level[ifend][int(row[0])]=int(row[1])
    # cl = []
    # for k,v in level[0].items():
    #     cl.append(level[1][v])

    # print(cl)
    # t_cl = []
    # for i in names:
    #     t_cl.append(cl[i])
    # print(t_cl)



    # g.write_edgelist('broadmann.txt')
    # print(cl)
    # igraph.plot(g)
    # cl = igraph.clustering(cl)
    # print(level)
    # temp = igraph.clustering.VertexClustering(g,membership=t_cl)
    # igraph.plot(temp)


def function_bnv_nii(net_path,outPath):   
    edges,vertex = [], []
    i = 0
    size = 0
    netthreshold = 0.4
    with open(net_path,'r') as f:
        for row in csv.reader(f.read().splitlines()):
            size = len(row)
            ifHasEdge = False
            for j in range(0,len(row)):
                if abs(float(row[j]))>netthreshold and j!=i:
                    if j>i:
                        edges.append((i,j,1/abs(float(row[j]))))
                    ifHasEdge = True
            if not ifHasEdge:
                print(i)
                vertex.append(i)
            i = i+1
    
    g = igraph.Graph.TupleList(edges, directed=False, vertex_name_attr='name', weights=True)
    g.add_vertices(vertex)
    # print(vertex)
    size = len(g.vs)
    # print(size)
    louvain_community = g.community_multilevel(weights=g.es['weight'])

    member = louvain_community.membership
    print(member,louvain_community.modularity)
    atl = path.curatlas()
    re = [atl.ticks[i] for i in g.vs['name']]
    names = g.vs['name']
    color_atlas_region(atlasobj=atl,regions=re,colors=[member[i]+1 for i in range(len(member))],outfilepath=os.path.join(outPath,'community_hub_{}.nii'.format(netthreshold)),resolution="3mm")
    curNodeData = atl.bnvnode.nodedata


    color = ncolors(louvain_community._len) 
    visual_style = {} 
    visual_style["vertex_color"] = [color[member[i]] for i in range(size)]
    visual_style["vertex_label"] = g.vs["name"]  

    # bc_path = os.path.join(outPath,"bold_net_attr","inter-region_bc_hub.csv")
    # bc_temp = []
    # with open(bc_path,'r') as f:
    #     for row in csv.reader(f.read().splitlines()):
    #         for i in row:
    #             bc_temp.append(int(i))

    bc_temp = g.betweenness(weights=g.es['weight'])
    

    temp_np = np.array(bc_temp)
    temp_np = (temp_np-temp_np.min())/(temp_np.max()-temp_np.min())*20+15
    max_size = temp_np.max()
    for i in range(size):
        # curNodeData[names[i]][4],curNodeData[names[i]][3] = str(bc_temp[names[i]]),str(member[i]+1)
        curNodeData[names[i]][4],curNodeData[names[i]][3] = str(temp_np[i]),str(member[i]+1) #bc和curnodedata同顺序
        # curNodeData[names[i]][4],curNodeData[names[i]][3] = str(temp_np[names[i]]),str(member[i]+1) #bc和curnodedata同顺序
    
    bc = {}
    for i in range(size):
        if member[i] not in bc.keys():
            bc[member[i]] = {}
        bc[member[i]][i] = bc_temp[names[i]]

    # print(visual_style['vertex_color'])
    for v in bc.values():
        visual_style['vertex_color'][max(v,key=lambda s:v[s])] = 'white'

    for v in bc.values():
        curNodeData[names[max(v,key=lambda s:v[s])]][4] = str(max_size+5)
    
    with open(os.path.join(outPath,'community_hub_{}vis.node'.format(netthreshold)),'w') as f:
        for i in range(size):
            content = "\t".join(curNodeData[i])+"\n"
            f.write(content)
    
    # igraph.plot(louvain_community,**visual_style).save(os.path.join(outPath,'community_hub_{}.png'.format(netthreshold)))


  
def inter_calc():
    print(os.getcwd())
    corrcoef_path = os.path.join(os.getcwd(),'bold_net','corrcoef.csv')
    outfolder = os.getcwd()
    print(outfolder)

    print(corrcoef_path)
    if not os.path.isdir(outfolder):
        os.mkdir(outfolder)
    # function(corrcoef_path,outfolder)
    function_bnv_nii(corrcoef_path,outfolder)
            


def bnvPlot():
    nodeFileName = "community_hub_0.4vis.node"
    nodePath = os.path.join(os.getcwd(),nodeFileName)
    # cfgPath = "E:\\xu_fMRI\\hub0924.mat"
    cfgPath = "F:\\zhangziliang\\wangxiuhua\\wangxiuhua_with.mat"
    bnvMesh = "BrainMesh_ICBM152_smoothed.nv"
    outPath = os.path.join(os.getcwd(),"hub0.4_with.png")
    title = "F:\\zhangziliang\\wangxiuhua\\normalized_wangxiuhua_lesion.nii"
    # mstr = bnv.gen_matlab(nodepath=nodePath,outpath=outPath,bnv_mesh=bnvMesh,bnv_cfg=cfgPath,edgepath=" ",title=" ")
    mstr = bnv.gen_matlab(nodepath=nodePath,outpath=outPath,bnv_mesh=bnvMesh,bnv_cfg=cfgPath,edgepath=" ",title=title)

    j = job.MatlabJob('bnv',mstr)
    print(mstr)
    j.run()



def hubStatistic(folder,atlasPath,namePath):
    atlasList = load_txt(atlasPath)
    nameList = load_txt(namePath)
    bnvnodeName = "community_hub_0.4vis.node"
    import collections
    outcome =collections.defaultdict(list)
    for atlas in atlasList:
        hubcount = []
        for name in nameList:

            bnvnodePath = os.path.join(folder,name,atlas,bnvnodeName)
            bnvnode = bnv.BNVNode(bnvnodePath)
            if not hubcount:
                hubcount = [0]*len(bnvnode.nodedata)
            for i in range(len(bnvnode.nodedata)):
                if abs(float(bnvnode.nodedata[i][4])-40)<10e-5:
                    hubcount[i]+=1
        outcome[atlas] = hubcount
    
    import matplotlib.pyplot as plt
    for k,v in outcome.items():
        plt.figure()
        plt.bar(list(range(len(v))),v)
        plt.title(k)
        plt.savefig("E:\\xu_fMRI\\"+k+".png")

            
                    
                    
                    
                

    pass



if __name__=="__main__":
	# inter_calc()
    bnvPlot()

    # hubStatistic("E:\\DataProcessing\\BOLD\\","E:\\xu_fMRI\\atlasList6.txt","E:\\xu_fMRI\\tfMRI_scanlist_DPARSFA_RL.txt")


