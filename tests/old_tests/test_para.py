from mmdps.proc import para
import time
import random


def f(arg):
    print(arg)
    i = random.randint(100, 1000)
    time.sleep(i / 100)

if __name__ == '__main__':
    argvec = ['job'+str(i) for i in range(20)]
    para.run(f, argvec)
    
