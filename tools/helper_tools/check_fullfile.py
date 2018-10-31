
import sys
from mmdps.util import path


if __name__ == '__main__':
    if len(sys.argv) == 2:
        file = sys.argv[1]
        
        full = path.fullfile(file)
        print(full)
        
