#coding: utf-8
import types, copy, os
from decimal import Decimal
from context import Context

class DbObj(object):
    "数据映射对象(ORM)"
    TABLE_NAME = ""
    PK_NAME = None
    EVENT_ROOT = ""
    CACHE_NAME = ""

    def __init__(self, context, pk, data={}):
        assert isinstance(context, Context)
        assert context.db!=None
 
        self._ctx = context
        self._dirty = False
        self._data = copy.copy(data)

        if len(data)==0:
            if type(self.PK_NAME) in (types.TupleType, types.ListType):
                assert type(pk)==types.DictType
                for n in self.PK_NAME:
                    self._data[n] = pk[n]
                    setattr(self, n, pk[n])
            else:
                self._data[self.PK_NAME] = pk
                setattr(self, self.PK_NAME, pk)

            self.load()
        else:
            for k,v in data.items():
                setattr(self, k, v)

    @classmethod
    def sql(cls):
        raise NotImplementedError

    @classmethod
    def pk2sql(cls, pks):
        assert cls.PK_NAME!=None

        if type(pks) not in (types.TupleType, types.ListType):
            pks = [pks]

        if type(cls.PK_NAME) in (types.TupleType, types.ListType):
            ors = []
            for p in pks:
                aa = []
                for k in cls.PK_NAME:
                    v = p[k]
                    if type(v)==types.IntType:
                        v = str(v)
                    elif type(v)==types.UnicodeType:
                        v = "'%s'" % v.encode("utf-8")
                    elif type(v)==types.StringType:
                        v = "'%s'" % v
                    else:
                        raise NotImplementedError
                    aa.append("%s=%s" % (k,v))
                ors.append(" and ".join(aa))

            return " or ".join("(%s)" % x for x in ors)
        else:
            lst = []
            for v in pks:
                if type(v)==types.IntType:
                    v = str(v)
                elif type(v)==types.UnicodeType:
                    v = "'%s'" % v.encode("utf-8")
                elif type(v)==types.StringType:
                    v = "'%s'" % v
                else:
                    raise NotImplementedError
                lst.append(v)

            if len(lst)>1:
                return "%s in (%s)" % (cls.PK_NAME, ",".join(lst))
            else:
                return "%s=%s" % (cls.PK_NAME, lst[0])

    @classmethod
    def load_many(cls, ctx, pks):
        "载入多个对象"
        s = cls.sql()
        w = cls.pk2sql(pks)
        if "where" in s:
            s += " and %s" % w
        else:
            s += " where %s" % w

        lst = []
        for r in ctx.db.fetchAll(s):
            lst.append(cls(ctx, None, data=r))
        return lst


    def load(self):
        "载入对象"
        assert self.PK_NAME!=None
        self._dirty = False

        for k in self._data:
            if k!=self.PK_NAME and k not in self.PK_NAME:
                delattr(self, k)

        if type(self.PK_NAME) in (types.TupleType, types.ListType):
            for n in self.PK_NAME:
                self._data[n] = getattr(self, n)
        else:
            self._data[self.PK_NAME] = getattr(self, self.PK_NAME)
 
        self.init()

        if len(self._data)>0:
            for k, v in self._data.items():
                if isinstance(v, Decimal): v = float(v)
                #if type(v)==types.FloatType: v=Decimal("%.4f" % v)
                setattr(self, k, v)
        else:
            if type(self.PK_NAME) in (types.TupleType, types.ListType):
                for n in self.PK_NAME:
                    setattr(self, n, None)
            else:
                setattr(self, self.PK_NAME, None)

    reload = load

    def init(self):
        "从数据库初始化数据"
        raise NotImplementedError

    def _is_null(self): return len(self._data)==0
    is_null = property(_is_null)

    def keys(self):
        return self._data.keys()

    def has_key(self, k):
        return self._data.has_key(k)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def get_pk(self):
        "返回对象的PK值"
        if type(self.PK_NAME) in (types.TupleType, types.ListType):
            return dict((x, self.get(x)) for x in self.PK_NAME)
        else:
            return self.get(self.PK_NAME)

    def do_drop(self):
        "删除表中记录"
        if not self.is_null and self.TABLE_NAME!="":
            if type(self.PK_NAME) in (types.TupleType, types.ListType):
                ns = self.PK_NAME
            else:
                ns = [self.PK_NAME]
            s = "delete from %s where %s" % (self.TABLE_NAME, " and ".join("%s=%%(s)%s" % (x,x) for x in ns))
            d = dict((x, self._data.get(x)) for x in ns)
            self._ctx.db.execute(s, d)
        else:
            raise NotImplementedError

    def assemble_event(self, verb):
        if self.EVENT_ROOT!="":
            return "%s.%s" % (self.EVENT_ROOT, verb)
        else:
            return ""

    @classmethod
    def get_obj_pool(cls, ctx, cache_name=None):
        "返回对象缓存"
        if cache_name==None: 
            cn = cls.CACHE_NAME
        else:
            cn = cache_name
        if cn=="": cn="%s:%s" % (os.path.abspath(__file__), cls.__name__)
        cache_name = "obj-pool-%s" % cn
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
    def get_from_pool(cls, ctx, pk):
        "按PK值从缓存载入对象"
        cache = cls.get_obj_pool(ctx)
        if type(cls.PK_NAME) in (types.TupleType, types.ListType):
            key = tuple(pk[x] for x in cls.PK_NAME)
        else:
            key = pk
        return cache.get(key)

    @classmethod
    def put_into_pool(cls, ctx, pk, obj, cache_name=None):
        "按PK值加入缓存对象"
        cache = cls.get_obj_pool(ctx, cache_name=cache_name)
        if type(cls.PK_NAME) in (types.TupleType, types.ListType):
            key = tuple(pk[x] for x in cls.PK_NAME)
        else:
            key = pk
        cache[key] = obj

    @classmethod
    def expire_pool(cls, ctx, pk):
        "缓存失效"
        cache = cls.get_obj_pool(ctx)
        if type(cls.PK_NAME) in (types.TupleType, types.ListType):
            key = tuple(pk[x] for x in cls.PK_NAME)
        else:
            key = pk
        if key in cache:
            del cache[key]

    @classmethod
    def get_instance(cls, ctx, pk):
        "按PK值载入对象"
        o = cls.get_from_pool(ctx, pk)
        if o!=None: return o

        o = cls(ctx, pk)
        if o.is_null: o = None
        if o!=None: cls.put_into_pool(ctx, pk, o)
        return o

    @classmethod
    def drop(cls, ctx, x):
        if (isinstance(x, cls)):
            o = x
            pk = x.get_pk()
        else:
            o = cls.get_instance(ctx, x)
            pk = x

        if o!=None:
            if type(cls.PK_NAME) in (types.TupleType, types.ListType):
                key = tuple(pk[x] for x in cls.PK_NAME)
            else:
                key = pk

            evt = o.assemble_event('drop')
            o.do_drop()
            cache = cls.get_obj_pool(ctx)
            if key in cache: del cache[key]
            ctx.signal(evt, pk)

