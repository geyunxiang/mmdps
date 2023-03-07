from json import load
import os 
from mmdps.util import path
from mmdps.util.loadsave import load_json

def check_args(args,restrict):
    for k in restrict:
        if k not in args.keys():
            raise Exception('Required Key missing Error: {}'.format(k))
    

def changeOutputName(args):
    _tmp = args["segOutputName"].split('.')[0]
    if args['t1Level'] and args['t2Level']:
        _tmp = '_'.join([_tmp,str(args['t1Level']),str(args['t2Level'])])
    args["segOutputName"] = _tmp+'.img'

    _tmp = args["maskOutputName"].split('.')[0]
    if args['t1Level'] and args['t2Level']:
        _tmp = '_'.join([_tmp,str(args['t1Level']),str(args['t2Level'])])
    if args['maskThreshold']:
        _tmp = '_'.join([_tmp,str(args['maskThreshold'])])
    args["maskOutputName"] = _tmp+'.img'

    return args

def autoseg(args):
    _exePath = path.fullfile('autoseg.exe')
    _t1imgPath = os.path.join(os.getcwd(),args['T1InputName'])
    _t2imgPath = os.path.join(os.getcwd(),args['T2InputName'])
    _resultPath = os.path.join(os.getcwd(),args['segOutputName'])
    _t1Level = str(args['t1Level'])
    _t2Level = str(args['t2Level'])
    if _t1Level and _t2Level:
        _cmdline = [_exePath, _t1imgPath, _t2imgPath, _resultPath,_t1Level,_t2Level]
    else:
        _cmdline = [_exePath, _t1imgPath, _t2imgPath, _resultPath]
    _cmdline = ' '.join(_cmdline)
    os.system(_cmdline)


def mask(args):
    _exePath = path.fullfile('mask.exe')
    _segImgPath = os.path.join(os.getcwd(),args['segOutputName'])
    _resultPath = os.path.join(os.getcwd(),args['maskOutputName'])
    _threshold = str(args['maskThreshold'])
    _cmdline = " ".join([_exePath,_segImgPath,_resultPath,_threshold])
    os.system(_cmdline)
    pass

def run(args):
    autoseg(args)
    mask(args)


if __name__ == '__main__':
    os.chdir('D:\\zhangziliang\\GitWorkspace\\tumor_test_data\\xxx\\')
    args = load_json(path.fullfile('tumorSeg&Mask.json'))
    configRestrict = ["T1InputName","T2InputName", "segOutputName", "t1Level", "t2Level", "maskOutputName", "maskThreshold"]
    check_args(args,configRestrict)
    args = changeOutputName(args)
    run(args)
    pass