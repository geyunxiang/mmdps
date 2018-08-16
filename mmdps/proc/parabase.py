"""Parallel base functions.

Useful functions to run commands in parallel.
If you have a lot of time consuming work to run, save the function
handles to a list, and use tools in this module to run them in 
parallel.

Example:
allfuncs = []
allfuncs.append(plot_heatmap.run)
allfuncs.append(plot_line.run)
allfuncs.append(plot_bnv.run)
allfuncs.append(plot_circos.run)
parabase.run_callfunc(allfuncs)
"""

import multiprocessing
import threading
import time
import os
import queue
# from ..util import clock
from mmdps.util import clock

class FWrap:
	"""Wrap the function in an object. Put run arg in the q when done."""
	def __init__(self, f, q):
		"""Init the FWrap using function to run and queue."""
		self.f = f
		self.q = q
		
	def run(self, arg):
		"""Run the function. Put the run arg to q when finished calling f."""
		res = self.f(arg)
		self.q.put(arg)
		return res

def get_processes(processes):
	"""Get how many processes to use when run things in parallel.
	
	Set env MMDPS_CPU_COUNT=n to force the cpu count to n. n is an integer.
	"""
	if processes:
		return processes
	else:
		cpu_count = os.cpu_count()
		cpu_count = cpu_count // 2
		if cpu_count == 0:
			cpu_count = 1
		cpu_count = int(os.getenv('MMDPS_CPU_COUNT', cpu_count))
		print('Processes count:', cpu_count)
		return cpu_count

def run1(f, argvec, processes=None):
	"""Run function f len(argvec) times, each time use one arg in argvec."""
	processes = get_processes(processes)
	with multiprocessing.Pool(processes) as p:
		m = multiprocessing.Manager()
		q = m.Queue()
		fwrap = FWrap(f, q)
		result = p.map_async(fwrap.run, argvec)
		ntotal = len(argvec)
		print('Begin proc, {} cpus, {} left, start at {}'.format(processes, ntotal, clock.now()))
		nfinished = 0
		while True:
			if result.ready():
				break
			else:
				res = q.get()
				nfinished += 1
				print('{} just finished. {} left, at {}'.format(res, ntotal-nfinished, clock.now()))
		print('End proc, end at {}'.format(clock.now()))
		outputs = result.get()
		return outputs

def run(f, argvec, processes=None):
	"""Run function f len(argvec) times, each time use one arg in argvec."""
	processes = get_processes(processes)
	with multiprocessing.Pool(processes) as p:
		m = multiprocessing.Manager()
		q = m.Queue()
		fwrap = FWrap(f, q)
		result = p.map_async(fwrap.run, argvec)
		ntotal = len(argvec)
		print('Begin proc, {} cpus, {} left, start at {}'.format(processes, ntotal, clock.now()))
		nfinished = 0
		while True:
			if result.ready():
				break
			else:
				try:
					res = q.get(timeout=1)
				except queue.Empty:
					continue
				else:
					nfinished += 1
					print('{} just finished. {} left, at {}'.format(res, ntotal-nfinished, clock.now()))
		print('End proc, end at {}'.format(clock.now()))
		outputs = result.get()
		return outputs

def run_simple(f, argvec, processes=None):
	"""Same as run, without progress reporting."""
	processes = get_processes(processes)
	with multiprocessing.Pool(processes) as p:
		result = p.map(f, argvec)
		return result

def run_in_background(f, *args, **kwargs):
	"""Run f in background."""
	t = threading.Thread(target=f, args=args, kwargs=kwargs)
	t.setDaemon(True)
	t.start()

def callrun(o):
	"""Call o.run()."""
	o.run()

def callfunc(f):
	"""Call f()."""
	f()

def run_callrun(tasks):
	"""Parallel call run, call task.run() for each task in tasks.
	
	Use this whenever possible.
	"""
	run(callrun, tasks)

def run_callfunc(fs):
	"""Parallel call function, call f.() for each f in fs.
	
	Use this whenever possible.
	"""
	run(callfunc, fs)
