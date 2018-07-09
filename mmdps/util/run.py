"""Run command.

"""

import os
import sys
import subprocess

def popen(cmdlist):
    """Popen cmdlist."""
    return subprocess.Popen(cmdlist)

def pyexe():
    """Python executable path."""
    return sys.executable

def pyshellexe():
    """Python python.exe path."""
    pyshell = os.path.join(os.path.dirname(sys.executable), 'python.exe')
    return pyshell

def popen_py(cmdlist, usepyshell=False):
    """Popen python script."""
    if usepyshell:
        p = pyshellexe()
    else:
        p = pyexe()
    fullcmdlist = [p]
    fullcmdlist.extend(cmdlist)
    return popen(fullcmdlist)

def call_py(cmdlist, usepyshell=False):
    """Call python cmdlist."""
    if usepyshell:
        p = pyshellexe()
    else:
        p = pyexe()
    fullcmdlist = [p]
    fullcmdlist.extend(cmdlist)
    return call(fullcmdlist)
    
def call(cmdlist):
    """Call cmdlist."""
    try:
        ret = subprocess.check_output(cmdlist, stderr=subprocess.STDOUT)
        output = ret
        retcode = 0
    except subprocess.CalledProcessError as err:
        output = err.output
        retcode = err.returncode
        print('ERROR')
    print(retcode)
    print(output)
    return retcode
