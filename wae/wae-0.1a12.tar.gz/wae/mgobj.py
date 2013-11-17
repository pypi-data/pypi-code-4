#coding:utf-8
from wae.context import BaseContext
import pymongo, pymongo.database
import UserDict
import types, copy, os
from bson.objectid import ObjectId
OID = ObjectId

class MongoObj(UserDict.IterableUserDict):
    """MongoDB文档对象"""

    COLLECTION_NAME = ""
    """集合名"""

    CKEYS = []
    """除_id外，自定义主键表"""

    defaults = {}
    """属性默认值"""

    def __init__(self, ctx, **data):
        """@param collection: 本对象映射对应的MongoDB集合
           @keyword data: 文档初始化数据"""
        assert self.COLLECTION_NAME!=""
        assert isinstance(ctx, BaseContext), ctx
        for k in self.CKEYS:
            assert k in data

        # 更新默认值
        for k, v in self.defaults.items():
            if k not in data:
                data[k] = copy.deepcopy(v)

        UserDict.IterableUserDict.__init__(self, data)
        self._ctx = self.ctx = ctx 
        self._collection = ctx.mongodb[self.COLLECTION_NAME]

    def __getitem__(self, key):
        val = UserDict.IterableUserDict.__getitem__(self, key)
        #if type(val)==types.DictType and not isinstance(val, MgDict):
        #    val = MgDict(self, val)
        #    UserDict.IterableUserDict.__setitem__(self, key, val)
        return val

    def __setitem__(self, key, val):
        assert key not in self.CKEYS
        assert key!="_id"
        assert "." not in key
        assert "$" not in key
        #if type(val)==types.DictType and not isinstance(val, MgDict):
        #    val = MgDict(self, val)
        UserDict.IterableUserDict.__setitem__(self, key, val)

    def __repr__(self):
        return "<%s instance at 0x%x %s>" % (self.__class__.__name__, id(self), UserDict.IterableUserDict.__repr__(self))

    def _get_id(self): return self.get("_id")
    id = property(_get_id)

    def is_stored(self): 
        """判断本文档对象是否已保存到MongDB
           @rtype: bool"""
        return "_id" in self
    stored = property(is_stored)

    def reload(self):
        """重新载入数据"""
        assert "_id" in self
        d = self._collection.find_one({"_id":self["_id"]})
        if d!=None:
            self.data = d
            return True
        else:
            self.clear()
            return False

    def before_save(self):
        pass

    def save(self):
        """保存到MongoDB，如果记录不存在，自动创建"""
        self.before_save()

        d = self.data
        #d['$atomic'] = 1
        i = self._collection.save(d)

        if "_id" not in self:
            self.data = self._collection.find_one({"_id":i})
        else:
            assert str(i)==str(self['_id']), (i, self["_id"])
        return self['_id']


    @classmethod
    def load(cls, ctx, _id):
        """通过_id加载对象"""
        data = ctx.mongodb[cls.COLLECTION_NAME].find_one({"_id":_id})
        if data!=None:
            return cls(ctx, **data)
        else:
            return None

    @classmethod
    def find(cls, ctx, cond={}, sort=None, skip=0, limit=0):
        """查询并返回对象列表
           keyword cond: 查询条件 e.g: {"name1":val1, "name2":{"$gt":val2}}
           keyword sort: 排序 [(name1, 1), (name2, -1) ...]
           @rtype: list"""
        assert isinstance(ctx, BaseContext)
        rs = ctx.mongodb[cls.COLLECTION_NAME].find(cond)
        if sort!=None: rs.sort(sort)
        if skip>0: rs.skip(skip)
        if limit>0: rs.limit(limit)
        return [cls(ctx, **x) for x in rs]

    @classmethod
    def find2(cls, ctx, conds, skip=0, limit=0):
        """查询并返回对象列表
           @rtype: list"""
        cc = copy.deepcopy(conds[0].dict())
        if len(conds)>1:
            for cond in conds[1:]:
                for k, v in cond.dict().items():
                    if k not in cc:
                        cc[k] = copy.deepcopy(v)
                    else:
                        if type(cc[k])==types.DictType:
                            cc[k] = copy.deepcopy(v)
                        else:
                            cc[k] = {k:copy.deepcopy(v)}

        rs = ctx.mongodb[cls.COLLECTION_NAME].find(cc)
        if skip>0: rs.skip(skip)
        if limit>0: rs.limit(limit)
        return [cls(ctx, **x) for x in rs]

    @classmethod
    def get_obj_pool(cls, ctx):
        "返回对象缓存"
        cn="%s:%s" % (os.path.abspath(__file__), cls.__name__)
        cache_name = "mgobj-pool-%s" % cn
        if not ctx.has_key(cache_name): ctx.set(cache_name, {})
        return ctx.get(cache_name)

    @classmethod
    def reload_obj_pool(cls, ctx):
        "重新载入缓存中某类型的对象"
        cache = cls.get_obj_pool(ctx)
        for o in cache.values():
            if isinstance(o, cls):
                o.reload()

    @classmethod
    def reset_obj_pool(cls, ctx):
        "清空缓存对象"
        cache = cls.get_obj_pool(ctx)
        cache.clear()

    @classmethod
    def get_from_pool(cls, ctx, _id):
        "按_id值从缓存载入对象"
        cache = cls.get_obj_pool(ctx)
        return cache.get(str(_id))

    @classmethod
    def put_into_pool(cls, ctx, obj):
        "加入缓存对象"
        assert "_id" in obj
        cache = cls.get_obj_pool(ctx)
        cache[str(obj['_id'])] = obj

    @classmethod
    def expire_pool(cls, ctx, _id):
        "缓存失效"
        cache = cls.get_obj_pool(ctx)
        key = str(_id)
        if key in cache: del cache[key]

    @classmethod
    def get_instance(cls, ctx, _id):
        "按_id载入对象"
        o = cls.get_from_pool(ctx, _id)
        if o!=None: return o

        o = cls.load(ctx, _id)
        if o!=None: cls.put_into_pool(ctx, o)
        return o

    @classmethod
    def drop(cls, ctx, x):
        if (isinstance(x, cls)):
            o = x
            _id = x["_id"]
        else:
            o = cls.get_instance(ctx, x)
            _id = x

        if o!=None:
            cache = cls.get_obj_pool(ctx)
            key = str(_id)
            if key in cache: 
                del cache[key]['_id']
                del cache[key]

        ctx.mongodb[cls.COLLECTION_NAME].remove({"_id":_id})


'''
class MgDict(UserDict.IterableUserDict):
    def __init__(self, mgobj, data):
        assert isinstance(mgobj, MongoObj)
        assert type(data)==types.DictType
        self._mongo_obj = mgobj
        UserDict.IterableUserDict.__init__(self, data)

    def __getitem__(self, key):
        val = UserDict.IterableUserDict.__getitem__(self, key)
        if type(val)==types.DictType:
            val = MgDict(self._mongo_obj, val)
        return val
 
    def __setitem__(self, key, val):
        if isinstance(val, MgDict): val = val._data
        self._data[key] = val

    def __delitem__(self, key):
        super(MgDict, self).__delitem__(key)

    def get(self, key, default=None):
        val = UserDict.IterableUserDict.get(self, key, default)
        if type(val)==types.DictType:
            val = MgDict(self._mongo_obj, val)
        return val

    def items(self):
        lst = []
        for k, v in UserDict.IterableUserDict.items(self):
            if type(v)==types.DictType:
                v = MgDict(self._mongo_obj, v)
            lst.append((k, v))
        return lst

    def values(self):
        lst = []
        for v in UserDict.IterableUserDict.values(self):
            if type(v)==types.DictType:
                v = MgDict(self._mongo_obj, v)
            lst.append(v)
        return lst
'''


class Property(object):
    """文档属性对象"""

    def __init__(self, name):
        self.name = name
        self.ops = {}

    def __eq__(self, v):
        self.ops[""] = v
        return self

    def __nq__(self, v):
        self.ops["$ne"] = v
        return self

    def __gt__(self, v):
        self.ops["$gt"] = v
        return self

    def __ge__(self, v):
        self.ops["$gte"] = v
        return self

    def __lt__(self, v):
        self.ops["$lt"] = v
        return self

    def __le__(self, v):
        self.ops["$lte"] = v
        return self

    def all(self, seq):
        self.ops["$all"] = seq
        return self

    def exists(self, yn):
        self.ops["$exists"] = bool(yn)
        return self

    def regex(self, pat):
        self.ops["$regex"] = pat

    def in_(self, *seq):
        self.ops["$in"] = seq
        return self

    def nin(self, seq):
        self.ops["$nin"] = seq
        return self

    def size(self, n):
        self.ops["$size"] = n
        return self

    def dict(self):
        ret = None
        for k, v in self.ops.items():
            if k=="":
                ret = v
            else:
                if type(ret)!=types.DictType:
                    ret = {k:v}
                else:
                    ret[k] = v
        return {self.name:ret}

    def __repr__(self):
        return "<Property instance '%s': %s>" % (self.name, str(self))

    def __str__(self):
        return repr(self.dict())

P = Property
"""快捷方式"""

'''
class Transformer(pymongo.son_manipulator.SONManipulator):
    """MongoDB数据和MongoObj对象转换器"""

    COLLECTION_NAME_TO_CLASS = {}
    """集合名到对象类型映射字典"""

    def transform_incoming(self, son, collection):
        d = {}
        for key, val in son.items():
            if isinstance(val, MgDict):
                d[key] = val.as_basic_dict()
            else:
                d[key] = val
        return d

    def transform_outgoing(self, son, collection):
        if collection.name in self.COLLECTION_NAME_TO_CLASS:
            cls = self.COLLECTION_NAME_TO_CLASS[collection.name]
            return cls(collection.database, **son)
        else:
            return son
'''
