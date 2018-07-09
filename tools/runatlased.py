"""Run atlased, possibly in parallel.

Set MMDPS_CUR_ATLAS per process, and run the pycmd.
"""
import os
import sys
import subprocess
import argparse

from mmdps.util.loadsave import load_txt
from mmdps.proc import atlas
from mmdps.proc import parabase, job


def popen_atlased(cmdlist, atlasname):
    newenv = os.environ.copy()
    newenv['MMDPS_CUR_ATLAS'] = atlasname
    p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=newenv)
    return p

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pycmd', help='python script to run, use atlas.getbyenv() inside', required=True)
    parser.add_argument('--atlaslist', help='txt contains atlas list', required=True)
    parser.add_argument('--parallel', action='store_true')
    args = parser.parse_args()

    ps = []
    cmdlist = [sys.executable]
    cmdlist.extend([args.pycmd])
    atlasnames = load_txt(args.atlaslist)
    if args.parallel:
        for atlasname in atlasnames:
            p = popen_atlased(cmdlist, atlasname)
            ps.append(p)
        print('dispatch...')
        for p in ps:
            stdout_data, stderr_data = p.communicate()
            print('process completed')
            print(p, stdout_data, stderr_data)
            print()
    else:
        for atlasname in atlasnames:
            p = popen_atlased(cmdlist, atlasname)
            stdout_data, stderr_data = p.communicate()
            print('process completed', atlasname)
            print(p, stdout_data, stderr_data)
            print()
            
        
    
