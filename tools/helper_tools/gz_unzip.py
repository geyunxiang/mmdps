import sys

from mmdps.util.fileop import gz_unzip

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: python gz_unzip.py file.gz')
		sys.exit(-1)

	gzfile = sys.argv[1]

	if gzfile[-3:] != '.gz':
		print('The file must end with .gz')
		sys.exit(-2)

	b = gz_unzip(gzfile)
	if b is None:
		sys.exit(-3)
