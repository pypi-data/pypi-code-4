#coding: utf-8
from multiprocessing import Process, Manager
from config import config
import pdo

def _db_query(mgr, name, host, user, password, dbname, sql):
    db = pdo.connect(host, user=user, password=password, dbname=dbname)
    try:
        mgr[name] = db.fetchAll(sql)
    except:
        import sys, traceback
        (tp, value, tb) = sys.exc_info()
        msg = '\n'.join(traceback.format_exception(tp, value, tb))
        mgr[name] = Exception(msg)


class ParelleQuery(object):
    "并行SQL查询"

    def __init__(self, named_sqls, timeout=None):
        self._sqls = named_sqls
        self.timeout = timeout

    def getdata(self):
        mgr = Manager()
        data = mgr.dict()
        procs = []

        for name, sql in self._sqls.items():
            args = (data, name, config.get('db', 'host'), config.get('db', 'user'), config.get('db', 'password'), config.get('db', 'dbname'), sql)
            p = Process(target=_db_query, args=args)
            p.start()
            procs.append(p)

        for p in procs:
            p.join(self.timeout)

        exs = {}
        for name, v in data.items():
            if isinstance(v, Exception):
                exs[name] = v.message
        if len(exs)>0:
            raise Exception(exs)

        return dict((k,v) for k,v in data.items())

