#coding: utf-8
import decimal
import collections
import types
import datetime
import json
from bson.objectid import ObjectId

def B(v, default=False):
    "转布尔"
    if v==None: return False
    if v in (True, False): return v

    if type(v) in (types.IntType, types.LongType):
        return v!=0
    else:
        v = str(v).lower()
        if v in ("1","t","y","true","yes"):
            return True
        elif v in ("0","f","n","false","no"):
            return False
        else:
            return default
    
def N(n, quant=None):
    """转换decimal"""
    assert quant==None or quant>=0
    if n==None: return None

    d = decimal.Decimal(str(n))
    if quant==None:
        return d
    else:
        if quant==0:
            q = "1"
        else:
            q = ".%s1" % ('0'*(quant-1))
        return d.quantize(decimal.Decimal(q))


def U(data):
    """转换unicode"""
    if isinstance(data, str):
        return unicode(data, "utf-8")
    elif isinstance(data, unicode):
        return data
    elif isinstance(data, decimal.Decimal):
        return float(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(U, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(U, data))
    else:
        return data


def U8(data):
    """数据转换为utf-8"""
    if isinstance(data, collections.Mapping):
        return dict((U8(key),U8(value)) for key, value in data.iteritems())
    elif isinstance(data, list):
        return [U8(element) for element in data]
    elif isinstance(data, unicode):
        return data.encode('utf-8')
    else:
        return data


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj.microsecond==0:
                return obj.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                return obj.strftime('%Y-%m-%dT%H:%M:%S.%f')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def exposed(*methods):
    """@expose装饰"""
    def _d(f):
        if len(methods)==0:
            mm = set(['GET','POST','PUT','DELETE'])
        else:
            mm = set(x.upper() for x in methods if x.upper() in ('GET','POST','PUT','DELETE'))
        setattr(f, "exposed", mm)
        return f
    return _d

def delegate(filename, classname):
    """@delegate装饰"""
    def _d(func):
        func.delegate = (filename, classname)
        return func
    return _d

