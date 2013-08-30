#!/usr/bin/env python
import multiprocessing as mp
from usher.tcp_client import UsherTCPClient

q = mp.Queue()

def action(host, port):
    cli = UsherTCPClient(host, port)
    r = cli.acquire_lease('/target', 5)
    q.put(r)

if __name__ == '__main__':
    import sys
    host = sys.argv[0]
    port = sys.argv[1]

    pool = mp.Pool(processes=5)
    for i in xrange(5):
        pool.apply_sync(action)
    pool.close()
    pool.join()
    total = [q.get() for i in xrange(5)]
    if total == 5:
        sys.exit(0)
    else:
        sys.exit(1)

