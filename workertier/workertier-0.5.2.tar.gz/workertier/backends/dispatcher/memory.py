#coding:utf-8
from workertier.backends.dispatcher import Dispatcher


class MemoryDispatcher(Dispatcher):
    def __init__(self, store, operation):
        self._store = store
        self._operation = operation
        self._consumers = []

    def dispatch(self, key):
        self._store[key] = self._operation(key)
        for consumer in self._consumers:
            consumer(key)

    def start_consumer(self, message_consumer):
        self._consumers.append(message_consumer)


