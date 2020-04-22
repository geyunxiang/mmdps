import sys

from mmdps.util.fileop import gz_zip

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: python gz_zip.py file')
		sys.exit(-1)

	gzfile = sys.argv[1]

	b = gz_zip(gzfile)
	if b is None:
		sys.exit(-3)
