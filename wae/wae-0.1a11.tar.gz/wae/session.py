#coding: utf-8
import uuid
import wae.connect
import datetime
import cPickle

class RedisSession(object):
    PREFIX = "wae-session-key"

    def __init__(self, db, sessid=None, expire=86400):
        import redis
        assert isinstance(db, redis.Redis)
        assert expire>0

        self._db = db
        self._expire = expire
        self._is_new = False

        if sessid!=None:
            k = "%s:%s" % (self.PREFIX, sessid)
            if not self._db.exists(k):
                sessid = None

        if sessid==None:
            self._is_new = True
            while True:
                sessid = str(uuid.uuid1())
                k = "%s:%s" % (self.PREFIX, sessid)
                if not self._db.exists(k):
                    self._db.set(k, 1)
                    break

        # 延长_expire失效
        self._db.expire(k, self._expire)
        self._id = sessid


    def _chk_is_new(self): return self._is_new
    is_new = property(_chk_is_new)

    def _get_id(self): return self._id
    sessid = property(_get_id)


    def put(self, key, value):
        assert isinstance(key, basestring) and key!="", key
        k = "%s:%s:%s" % (self.PREFIX, self.sessid, key)
        if value!=None: 
            v = cPickle.dumps(value)
            self._db.set(k, v)
            self._db.expire(k, self._expire)
        else:
            self._db.delete(k)

    def get(self, key, default=None):
        assert isinstance(key, basestring) and key!=""
        k = "%s:%s:%s" % (self.PREFIX, self.sessid, key)
        if not self._db.exists(k):
            return default
        else:
            v = self._db.get(k)
            self._db.expire(k, self._expire)
            try:
                return cPickle.loads(v)
            except:
                return default

    def keys(self):
        return self._db.keys("%s:%s*" % (self.PREFIX, self.sessid))

    def drop(self, *keys):
        self._db.delete(*keys)

    def has_key(self, key):
        k = "%s:%s:%s" % (self.PREFIX, self.sessid, key)
        return self._db.exists(key)


class BaseMongoSession(object):
    """使用MongoDB的session"""
    MONGO_COLLECTION = ""

    def __init__(self, sessid=None):
        assert self.MONGO_COLLECTION!=""

        _conn = wae.connect.connect_mongodb()
        self._sessdb = _conn[self.MONGO_COLLECTION]

        if sessid!=None:
            from bson.objectid import ObjectId
            try:
                _id = ObjectId(sessid)
            except:
                _id = sessid = None
        else:
            _id = None

        if _id==None or self._sessdb.session.find({"_id":_id}).count()==0:
            _id = self._sessdb.session.save({"ctime":datetime.datetime.now()})

        self._id = str(_id)

    def _get_id(self): return self._id
    sessid = property(_get_id)

    def get(self, key, default=None):
        assert isinstance(key, basestring) and key!=""
        #if key in self._cache: return self._cache[key]

        c = list(self._sessdb.cache.find({"sessid":self.sessid, "key":key}, {"value":1}).sort([("$natural",-1)]).limit(1))
        if len(c)==0:
            return default
        else:
            c = c[0].get("value")
            if c==None:
                return default
            else:
                try:
                    return cPickle.loads(c.encode("utf-8"))
                except:
                    return default 

    def put(self, key, value):
        assert isinstance(key, basestring) and key!=""
        c = {"sessid":self.sessid, "key":key}
        if value!=None: 
            c["value"] = cPickle.dumps(value)
            #if key in self._cache:
            #    del self._cache
        #else:
        #    self._cache[key] = value
        self._sessdb.cache.save(c)

    def drop(self, key):
        self.put(key, None)

    def has_key(self, key):
        return self.get(key)==None


class MongoSession(BaseMongoSession):
    MONGO_COLLECTION = "mba_sess"

