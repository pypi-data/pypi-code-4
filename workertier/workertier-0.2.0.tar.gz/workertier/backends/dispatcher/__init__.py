#coding:utf-8
class Dispatcher(object):
    def dispatch(self, key):
        raise NotImplementedError()

    def consume(self, consumer):
        raise NotImplementedError()

