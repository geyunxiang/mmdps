"""Job is a processing unit.

One job is a processing unit. It can run python script, matlab, 
executable, shell. It can run other jobs, forming a tree.
It can also run parallel, forming a project.
"""

import os
import sys
import warnings
import subprocess
import shlex
from collections import OrderedDict

# from ..util import clock, path
# from .. import rootconfig
from mmdps.util import clock, path
from mmdps import rootconfig

def genlogfilename(info=''):
	"""Generate a log file name base on current time and supplied info."""
	path.makedirs('log')
	timestr = clock.now()
	return 'log/log_{}_{}.txt'.format(timestr, info)

def call_logged2(cmdlist, info=''):
	"""Call the cmdlist and output the log to a file in log folder."""
	try:
		print(cmdlist)
		ret = subprocess.check_output(cmdlist, stderr=subprocess.STDOUT, stdin=None) #
		output = ret
		retcode = 0
	except subprocess.CalledProcessError as err:
		output = err.output
		retcode = err.returncode
		warnings.warn('Error run "{}", return code is {}'.format(str(cmdlist), retcode))
	with open(genlogfilename(info), 'wb') as f:
		f.write((str(cmdlist)+'\n\n').encode())
		f.write(output)
	return retcode

def call_logged(cmdlist, info=''):
	"""Call the cmdlist and output the log to a file in log folder."""
	logfilePath = genlogfilename(info)
	print('call_logged %s at %s' % (cmdlist, logfilePath))
	with open(logfilePath, 'w') as f:
		f.write(str(cmdlist)+'\n\n')
		f.flush()
		p = subprocess.Popen(cmdlist, stdout=f, stderr=f)
		p.communicate()
	retcode = p.returncode
	if retcode != 0:
		warnings.warn('Error run "{}", return code is {}'.format(str(cmdlist), retcode))
	return p.returncode

def call_in_wd(cmdlist, wd, info=''):
	"""Call in supplied working directory."""
	with ChangeDirectory(wd):
		retcode = call_logged(cmdlist, info)
	return retcode

class ChangeDirectory:
	"""Change dir context manager.

	Change to dir on enter, change back on exit.
	"""
	def __init__(self, chdirto):
		"""Init and change to dir chdirto."""
		self.oldfolder = os.getcwd()
		self.chdirto = chdirto

	def __enter__(self):
		"""When enter, change dir to."""
		os.chdir(self.chdirto)

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""When exit, change dir back."""
		os.chdir(self.oldfolder)
		
class Job:
	"""A job is a processing unit."""
	def __init__(self, name, cmd, config='', argv=None, wd='.'):
		"""Init the job with name, cmd, config, argv and wd.
		
		The config will become --config CONFIG in argv.
		wd is the working directory in which should be job run.
		"""
		self.name = name
		self.typename = type(self).__name__
		self.cmd = cmd
		self.config = config
		self.argv = argv if argv else ''
		if type(self.argv) is not str:
			self.argv = ' '.join([shlex.quote(s) for s in self.argv])
			print(self.argv)
		self.wd = wd

	@classmethod
	def from_dict(cls, d):
		"""Create the job from dict."""
		name = d.get('name', '')
		cmd = d.get('cmd', '')
		config = d.get('config', '')
		argv = d.get('argv', '')
		wd = d.get('wd', '.')
		o = cls(name, cmd, config, argv, wd)
		return o

	def to_dict(self):
		"""Serialize the job to dict."""
		d = OrderedDict()
		d['name'] = self.name
		d['typename'] = self.typename
		d['cmd'] = self.cmd
		d['config'] = self.config
		d['argv'] = self.argv
		d['wd'] = self.wd
		return d

	def build_fullcmd(self):
		"""Build full command.
		
		If the cmd is not absolute path, search in path for this cmd.
		It is similar to matlabpath, so you do not need to specify the
		full cmd path. Just make sure to avoid name clash.
		"""
		cmd = path.fullfile(self.cmd)
		if cmd:
			return cmd
		else:
			return self.cmd

	def build_fullconfig(self):
		"""Build full config.
		
		Search the config file using path.fullfile.
		"""
		config = path.fullfile(self.config)
		if config:
			return config
		else:
			return self.config

	def build_rootcmd(self):
		"""Build the root command."""
		rootcmd = [self.build_fullcmd()]
		return rootcmd

	def build_cmdlist(self):
		"""Build the command list, including rootcmd and argv."""
		cmdlist = self.build_rootcmd()
		cmdlist.extend(shlex.split(self.argv))
		if self.config:
			cmdlist.extend(['--config', self.build_fullconfig()])
		return cmdlist

	def run(self):
		"""Build cmd list and run the job in wd."""
		cmdlist = self.build_cmdlist()
		retcode = call_in_wd(cmdlist, self.wd, self.name)
		return retcode

class ShellJob(Job):
	"""Shell job."""
	def __init__(self, name, cmd, config='', argv=None, wd='.'):
		"""Init the shell job."""
		super().__init__(name, cmd, config, argv, wd)

class PythonJob(Job):
	"""Python job, run a python script.
	
	The script may be self-contained. If it use modules in the same directory,
	the directory should be added to project path so when run the job in wd,
	the python interpreter can import it.
	"""
	def __init__(self, name, cmd, config='', argv=None, wd='.'):
		"""Init the python job."""
		super().__init__(name, cmd, config, argv, wd)

	def build_rootcmd(self):
		"""Override the root cmd to python executable."""
		rootcmd = [rootconfig.path.python, self.build_fullcmd()]
		return rootcmd

class MatlabJob(Job):
	"""Matlab job, run a matlab string, typically a matlab function."""
	def __init__(self, name, cmd, config='', argv=None, wd='.'):
		"""Init the matlab job.
		
		The path.searchpathlist will be added to the matlab path by addpath function
		before the matlab command run. If not configured right, the matlab job cannot
		find the matlab function.
		"""
		super().__init__(name, cmd, config, argv, wd)

	def build_matlab_wd(self):
		"""Build wd, for matlab to cd into."""
		cwd = os.getcwd()
		wd = os.path.join(cwd, self.wd)
		return wd

	def build_matlab_logfile(self):
		"""Build matlab log file."""
		return genlogfilename('matlab_log')

	def matlab_path_to_add(self):
		"""Build the addpath command to add all paths in path.searchpathlist."""
		pathlist = path.searchpathlist()
		pathstrlist = ["'{}'".format(p) for p in pathlist]
		pathmatstr = ','.join(pathstrlist)
		finalstr = 'addpath(' + pathmatstr + ');'
		return finalstr

	def build_cmdlist(self):
		"""Build the full command line to run the matlab cmd."""
		cmdlist = []
		cmdlist.append(rootconfig.matlab_bin)
		cmdlist.extend(['-wait', '-nosplash', '-minimize', '-nodesktop', '-logfile',
				self.build_matlab_logfile(), '-r'])
		realcmd = []
		realcmd.append('"')
		realcmd.append(self.matlab_path_to_add())
		realcmd.append("try, ")
		realcmd.append("cd('{0}');".format(self.build_matlab_wd()))
		realcmd.append(self.cmd)
		realcmd.append(" ; catch me, fprintf('%s / %s', me.identifier, me.message), exit(-1), end, exit;")
		realcmd.append('"')
		realcmdstr = ''.join(realcmd)
		cmdlist.append(realcmdstr)
		return cmdlist

class ExecutableJob(Job):
	"""Executable job, this should be an executable."""
	def __init__(self, name, cmd, config='', argv=None, wd='.'):
		super().__init__(name, cmd, config, argv, wd)

class BatchJob(Job):
	"""Batch job, this is a list of sequentially run jobs."""
	def __init__(self, name, cmd, config='', argv=None, wd='.'):
		"""Init the batch job.
		
		If config is str, this is a configfile. If config is list, this list
		contains the children jobs in place.
		"""
		super().__init__(name, cmd, config, argv, wd)
		if type(config) is str:
			self.configtype = 'configfile'
		elif type(config) is list:
			self.configtype = 'joblist'
		else:
			raise Exception('Config should be a json file or python list')

	def run_configfile(self):
		"""Run config file, use runjob.py."""
		runbatchpath = os.path.join(rootconfig.path.tools, 'runjob.py')
		cmdlist = [sys.executable, runbatchpath]
		cmdlist.extend(shlex.split(self.argv))
		if self.config:
			cmdlist.extend(['--config', self.build_fullconfig()])
		retcode = call_in_wd(cmdlist, self.wd, self.name)
		return retcode

	def run_joblist(self):
		"""Run job list, one by one."""
		jobs = []
		for jobconfig in self.config:
			curjob = create(jobconfig)
			jobs.append(curjob)
		for curjob in jobs:
			retcode = curjob.run()
			if retcode != 0:
				return retcode
		return 0

	def run(self):
		"""Run the job. configfile or joblist."""
		if self.configtype == 'configfile':
			return self.run_configfile()
		else:
			return self.run_joblist()

# All the job classes        
JobClasses = [Job, ShellJob, PythonJob, MatlabJob, ExecutableJob, BatchJob]

# Class name to class mapping
JobClassesDict = {C.__name__: C for C in JobClasses}

def create(d):
	"""Create a job from dict."""
	typename = d['typename']
	C = JobClassesDict[typename]
	o = C.from_dict(d)
	return o

def dump(job):
	"""Dump the job to console."""
	return job.to_dict()

def load(d):
	"""Load a job from dict."""
	return create(d)

def runjob(job, folder=None):
	"""Run the job in folder."""
	if folder:
		with ChangeDirectory(folder):
			return job.run()
	else:
		return job.run()
