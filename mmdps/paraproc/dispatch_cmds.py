from multiprocessing import Pool
import os
import glob
import time
import datetime

def monitor_pool_map_async(mapres, refresh_interval=5):
	remaining = -1
	while True:
		if mapres.ready():
			break
		if remaining != mapres._number_left:
			remaining = mapres._number_left
			print(datetime.datetime.now().isoformat(), 'Waiting for', remaining, 'tasks to complete...')
		time.sleep(refresh_interval)
	print('All tasks have completed.')

def para_run_proc_in_folders(proc, folders, refresh_interval=5, ncpu=None):
	print("Start time:", datetime.datetime.now().isoformat())
	if ncpu:
		cpucount = ncpu
	else:
		cpucount = os.cpu_count()
		
	with Pool(cpucount) as p:
		mapres = p.map_async(proc, folders)
		monitor_pool_map_async(mapres, refresh_interval)

def seq_run_proc_in_folders(proc, folders):
	for folder in folders:
		proc(folder)
		print('End run proc in', folder)
		
if __name__ == '__main__':
	pass
	
