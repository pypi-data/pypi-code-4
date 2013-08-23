#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

class ResultProxy(object):
    @property
    def raw(self):
        return self._result if hasattr(self, '_result') else None

class Result(ResultProxy):
    def __init__(self, result=()):
        self._result = result or ()

    @classmethod
    def new(cls, result=()):
        return cls(result)

    def __iter__(self):
        return (RowResult.new(row) for row in self._result)

    def __getattr__(self, name):
        res = []
        for row in self._result:
            res.append(row.get(name))
        return res

class RowResult(ResultProxy):
    def __init__(self, result={}):
        self._result = result

    @classmethod
    def new(cls, result={}):
        return cls(result)

    def __getattr__(self, name):
        return self._result.get(name)

    def __iter__(self):
        return ((k, self._result[k]) for k in self._result)
