import sys

def setup_stdout(filename=''):
	if sys.stdout == None:
		sys.stdout = open(filename+'_stdout.txt', 'w')
	if sys.stderr == None:
		sys.stderr = open(filename+'_stderr.txt', 'w')
	return

def setup_stdout_force(filename=''):
	sys.stdout = open(filename+'_stdout.txt', 'w')
	sys.stderr = open(filename+'_stderr.txt', 'w')

def close_stdout():
	if sys.stdout:
		sys.stdout.close()
	if sys.stderr:
		sys.stderr.close()

		
