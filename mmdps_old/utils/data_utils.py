import shutil
import os
import gzip

def ungzip(fgz):
	with gzip.open(fgz, 'rb') as fin,\
		 open(fgz[:-3], 'wb') as fout:
		shutil.copyfileobj(fin, fout)

		
