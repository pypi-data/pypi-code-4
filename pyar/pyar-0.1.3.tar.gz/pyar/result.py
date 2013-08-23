#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

class ResultProxy(object):
    @property
    def raw(self):
        return self._result if hasattr(self, '_result') else None

    def __or__(self, other=None):
        if self.raw and len(self.raw) > 0:
            return self.raw
        if isinstance(other, ResultProxy):
            if len(other.raw) <= 0:
                return None
            return other.raw
        return other

class Result(ResultProxy):
    def __init__(self, result=()):
        self._result = tuple(result or ())

    @classmethod
    def new(cls, result=()):
        return cls(result)

    @classmethod
    def fromRowResult(self, rowResult=None):
        t = []
        if not isinstance(rowResult, RowResult):
            if rowResult is not None:
                raise TypeError("Class RowResult TypeError for '%s': " % rowResult)
        else:
            t = [rowResult.raw]
        return Result.new(tuple(t))

    def __iter__(self):
        return (RowResult.new(row) for row in self._result)

    def __getattr__(self, name):
        res = []
        for row in self._result:
            res.append(row.get(name))
        return res

    def __add__(self, other=None):
        if not isinstance(other, Result):
            if other is not None:
                raise TypeError("Class Result TypeError for '%s': " % other)
            else:
                return self

        return Result.new(self.raw + other.raw)

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

    def __add__(self, other=None):
        if not isinstance(other, RowResult):
            if other is not None:
                raise TypeError("Class RowResult TypeError for '%s': " % other)
            else:
                return Result.new(tuple([self.raw]))

        return Result.new(tuple([self.raw])) + Result.new(tuple([other.raw]))
