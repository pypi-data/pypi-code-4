#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

class ResultProxy(object):
    pass

class Result(ResultProxy):
    def __init__(self, result=()):
        self.result = result or ()

    @classmethod
    def new(cls, result=()):
        return cls(result)

    def __iter__(self):
        return (RowResult.new(row) for row in self.result)

    def __getattr__(self, name):
        res = []
        for row in self.result:
            res.append(row.get(name))
        return res

class RowResult(ResultProxy):
    def __init__(self, row={}):
        self.row = row

    @classmethod
    def new(cls, row={}):
        return cls(row)

    def __getattr__(self, name):
        return self.row.get(name)

    def __iter__(self):
        return ((k, self.row[k]) for k in self.row)
