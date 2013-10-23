#coding: utf-8
import connect
import pdo
import uuid

class BaseContext(object):
    "上下文环境"
    def __init__(self, **kwargs):
        self._items = kwargs
        self._cid = str(uuid.uuid1())

    def _get_id(self): return self._cid
    cid = property(_get_id)

    def get(self, key, default=None):
        return self._items.get(key, default)

    def set(self, key, val):
        self._items[key] = val
        try:
            setattr(self, key, val)
        except:
            pass

    def unset(self, key):
        if key in self._items:
            del self._items[key]
            try:
                delattr(self, key)
            except:
                pass

    def has_key(self, key):
        return self._items.has_key(key)

    def reset_obj_pool(self, ocls=None):
        """清除对象池"""
        for k in self._items.keys():
            if k.startswith("obj-pool-"):
                del self._items[k]

    def commit(self):
        pass

    def rollback(self):
        pass

    
class TenantContext(BaseContext):
    def __init__(self, tenant_id, **kwargs):
        super(TenantContext, self).__init__(**kwargs)
        self._tenant_id = tenant_id

    def _get_tenant_id(self): return self._tenant_id
    tenant_id = property(_get_tenant_id)


class Context(TenantContext):
    "上下文环境(with db, job and signal)"
    def __init__(self, tenant_id, db=None, **kwargs):
        super(Context, self).__init__(tenant_id, **kwargs)
        self._jobs = []
        self.signals = self._make_signal_publisher()
        if isinstance(db, pdo.Connection):
            self.db = db
        else:
            self.db = connect.connect_db()

    def _make_signal_publisher(self):
        from signal import SignalPublisher
        return SignalPublisher(tenant_id=self.tenant_id)

    def job(self, func, *args, **kwargs):
        "提交批处理作业"
        assert callable(func)
        for f, a, ka in self._jobs:
            if f==func and a==args and ka==kwargs:
                return
        self._jobs.append((func, args, kwargs))

    def commit(self):
        try:
            # 执行批处理作业
            while len(self._jobs)>0:
                j = self._jobs[0]
                self._jobs.remove(j)

                func, args, kwargs = j
                apply(func, args, kwargs)

            assert len(self._jobs)==0

            self.db.commit()        # 数据库提交
            self.signals.publish()  # 信号提交
        except:
            self.rollback()
            raise

    def rollback(self):
        self._jobs = []
        self.db.rollback()
        self.signals.reset()

    def close(self):
        self.db.close()
        del self.db
        self.signals.reset()

    def __del__(self):
        if getattr(self, 'db', None)!=None:
            self.db.close()
            del self.db

