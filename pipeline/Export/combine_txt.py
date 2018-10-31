from mmdps.util.loadsave import load_txt, save_txt

def combine_txts(outtxt, intxts):
    outset = set()
    for intxt in intxts:
        outset.update(load_txt(intxt))
    outlist = list(outset)
    outlist.sort()
    save_txt(outtxt, outlist)
    
if __name__ == '__main__':
    intxts = ['healthy.txt', 'paired_dianciji_duizhao.txt', 'paired_dianciji_zhiliao.txt',
              'paired_stroke.txt', 'scipatient.txt']
    combine_txts('entire.txt', intxts)
    
