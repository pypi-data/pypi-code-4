from __future__ import absolute_import
from Queue import Queue as _Queue

def _create(name, _global_queue_cache={}):
    if name not in _global_queue_cache:
        _global_queue_cache[name] = _Queue()
    return _global_queue_cache[name]

class Message:
    def __init__(self, queue, item):
        self.queue = queue
        self.item = item

    def getvalue():
        return self.item

    def __enter__(self):
        return self.item

    def __exit__(self, type, value, traceback):
        if value is not None:
            self.queue.put(self.item)


class Queue():
    def __init__(self, name):
        self.queue = _create(name)
    
    def next(self):
        item = self.get()
        if item:
            return Message(self,  item)
        else:
            raise StopIteration()

    def __iter__(self):
        return self 

    def get(self):
        return self.queue.get()
    
    def put(self, item):
        self.queue.put(item)
    
