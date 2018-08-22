import sys
import gzip
import shutil

from mmdps.util.fileop import gz_zip

    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python gunzip thefile.gz')
        sys.exit(-1)
        
    gzfile = sys.argv[1]
    
    if gzfile[-3:] != '.gz':
        print('The file must end with .gz')
        sys.exit(-2)
        
    b = gz_zip(gzfile)
    if b == None:
        sys.exit(-3)
        
