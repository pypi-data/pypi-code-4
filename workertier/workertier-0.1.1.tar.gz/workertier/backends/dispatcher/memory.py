#coding:utf-8
from workertier.backends.dispatcher import Dispatcher


class MemoryDispatcher(Dispatcher):
    def __init__(self, store, operation):
        self._store = store
        self._operation = operation

    def dispatch(self, key):
        self._store[key] = self._operation(key)


