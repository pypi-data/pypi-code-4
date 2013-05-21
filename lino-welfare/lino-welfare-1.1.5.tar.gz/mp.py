import time
from multiprocessing import Process
from multiprocessing import Pool

import threading


def f1():
    i = 0
    while True:
        i += 1
        print "server%d" % i
        time.sleep(1)

def f2():
    for i in range(5):
        print -i
        time.sleep(0.5)

if __name__ == '__main__':

    if False:
        pool = Pool(processes=2)
        r1 = pool.apply_async(f1)
        r2 = pool.apply_async(f2)
        print r1.get()
        print r2.get(timeout=5)
        pool.terminate()
        pool.join()
        
    if False:
        t = threading.Thread(target=server) # , [args=(), kwargs={}])
        t.start() # will run "foo"

        if not t.is_alive(): # will return whether foo is running currently
            raise Exception("server not alive")
            
        #~ t.join() # will wait till "foo" is done

        f2()
        t.stop()
        print "Done"
    
    #~ print r1, r2
    p = Process(target=f1)
    p.start()
    f2()
    #~ p.join()
    #~ p = Process(target=f2)
    #~ p.start()
    #~ p.join()
    p.terminate()
    

