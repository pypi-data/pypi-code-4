# coding: utf8

"""
    Thread pool for web tornado
"""

import threading
import Queue
import tornado.ioloop
from functools import partial

class ThreadPool():
    def __init__(self, pool_size=10):
        self._tasks = Queue.Queue()
        self._working = True

        # start threads
        for _ in xrange(pool_size):
            t = Worker(self)
            t.start()
    
    def stop(self):
        self._working = False
        self._tasks.put(['stop'])
    
    def execute(self, method, *argv, **kargs):
        callback = None
        if 'callback' in kargs:
            callback = kargs['callback']
            del kargs['callback']
        self._tasks.put(['execute', method, argv, kargs, callback])
    
    def send_result(self, task, result, error):
        callback = partial(task, (result, error))
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_callback(callback)

class Worker(threading.Thread):
    def __init__(self, cnt):
        self._controller = cnt
        super(Worker, self).__init__()
    def run(self):
        cnt = self._controller
        
        while cnt._working:
            task = cnt._tasks.get(True)
            command = task[0]
            if command == 'stop':
                cnt._tasks.put(['stop'])
                break

            result = None
            error = None
            try:
                method, argv, kargs, callback = task[1:]
                result = method(*argv, **kargs)
            except Exception as e:
                error = e
            if callback:
                cnt.send_result(callback, result, error)
