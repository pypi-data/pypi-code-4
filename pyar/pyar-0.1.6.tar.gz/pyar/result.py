#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

class ResultProxy(object):
    def raw(self):
        return self._result if hasattr(self, '_result') else None

    def __or__(self, other=None):
        if self.raw() and len(self.raw()) > 0:
            return self.raw()
        if isinstance(other, ResultProxy):
            if len(other.raw()) <= 0:
                return None
            return other.raw()
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
            t = [rowResult.raw()]
        return Result.new(tuple(t))

    def __iter__(self):
        return (RowResult.new(row) for row in self._result)

    def __getattr__(self, name):
        res = []
        for row in self._result:
            res.append(row.get(name))
        return res

    def __add__(self, other=None):
        u'''连接运算，other可类型为dict, RowResult, Result, None'''
        if isinstance(other, type(None)):
            return self
        elif isinstance(other, dict):
            _raw  = self | None
            _oraw = tuple([other])
            if _raw is None:
                if len(other) > 0:
                    return Result.new(_oraw)
                return None
            return Result.new(_raw + _oraw)
        elif isinstance(other, tuple):
            _raw = self | None
            if _raw is None:
                _raw = ()
            return Result.new(_raw + other)
        elif isinstance(other, list):
            _raw = self | None
            if _raw is None:
                _raw = ()
            return Result.new(_raw + tuple(other))
        elif isinstance(other, RowResult):
            _raw  = self | None
            _oraw = other | None
            if _raw is None:
                _raw = ()
            if _oraw is None:
                _oraw = ()
            else:
                _oraw = tuple([_oraw])
            return Result.new(_raw + _oraw)
        elif isinstance(other, Result):
            _raw  = self | None
            _oraw = other | None
            if _raw is None:
                _raw = ()
            if _oraw is None:
                _oraw = ()
            return Result.new(_raw + _oraw)
        else:
            raise TypeError("TypeError for '%s'." % other)

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
        u'''连接运算，other可类型为dict, RowResult, Result, None'''
        if isinstance(other, type(None)):
            return self
        elif isinstance(other, dict):
            _raw = self | None
            if _raw is None:
                if len(other) > 0:
                    return RowResult.new(other)
                return None
            _raw.update(other)
            return RowResult.new(_raw)
        elif isinstance(other, RowResult):
            _raw  = self | None
            _oraw = other | None
            if _raw is None:
                _raw = {}
            if _oraw is None:
                _oraw = {}
            _raw.update(_oraw)
            return RowResult.new(_raw)
        elif isinstance(other, Result):
            _raw  = self | None
            _oraw = other | None
            if _raw is None:
                _raw = ()
            else:
                _raw = tuple([_raw])
            if _oraw is None:
                _oraw = ()
            return Result.new(_raw + _oraw)
        else:
            raise TypeError("TypeError for '%s'." % other)
