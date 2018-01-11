import os
import sys
import subprocess

mmdpspath = os.getenv('MMDPS_PATH')
sys.path.insert(0, mmdpspath)
import mmdps_init as mi

def run_func_in_folder(folder, ffunc):
	oldfolder = os.getcwd()
	os.chdir(folder)
	ffunc()
	os.chdir(oldfolder)

def run_cmd_in_folder(folder, cmd, *args):
	oldfolder = os.getcwd()
	os.chdir(folder)
	cmdlist = [cmd]
	cmdlist.extend(tuple(args))
	p = subprocess.call(cmdlist)
	print('subprocess call returns', p)
	os.chdir(oldfolder)
	
def run_file_in_folder(folder, fbat):
	oldfolder = os.getcwd()
	os.chdir(folder)
	subprocess.run(fbat)
	os.chdir(oldfolder)
	
def run_py_in_folder(folder, fpy, *args):
	oldfolder = os.getcwd()
	os.chdir(folder)
	cmdlist = [sys.executable, fpy]
	cmdlist.extend(tuple(args))
	p = subprocess.call(cmdlist)
	print('subprocess call returns', p)
	os.chdir(oldfolder)

def run_pys_in_folder(folder, fpys, *args):
	oldfolder = os.getcwd()
	os.chdir(folder)
	for fpy in fpys:
		cmdlist = [sys.executable, fpy]
		cmdlist.extend(tuple(args))
		p = subprocess.call(cmdlist)
	os.chdir(oldfolder)
 
def build_matlab_cmd(folder, workmstr):
	cmd = []
	cmd.append(mi.matlab_bin)
	cmd.extend(['-wait', '-nosplash', '-minimize', '-nodesktop', '-logfile',
				'matlab_log.txt', '-r'])
	realcmd = []
	realcmd.append('"')
	realcmd.append("try, ")
	realcmd.append("cd('{0}');".format(folder))
	realcmd.append(workmstr)
	realcmd.append(" catch me, fprintf('%s / %s', me.identifier, me.message), exit(-1), end, exit;")
	realcmd.append('"')
	realcmdstr = ''.join(realcmd)
	cmd.append(realcmdstr)
	return cmd    
def run_matlab_in_folder(folder, workmstr):
	oldfolder = os.getcwd()
	os.chdir(folder)
	matlabcmd = build_matlab_cmd(folder, workmstr)
	p = subprocess.run(matlabcmd)
	print(p)
	os.chdir(oldfolder)
	
def get_subprocess_si(hidewindow=False):
	si = subprocess.STARTUPINFO()
	if hidewindow:
		si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	return si
