from docmongo.interfaces import IMongoDelegate
from zope.interface import implementer


@implementer(IMongoDelegate)
class DelegatePymongo(object):
    def __init__(self, host, dbname, colname):
        self.host = host
        self.dbname = dbname
        self.colname = colname

    def _delegate(self, func_name, *query, **kwquery):
        func = getattr(self.db(), func_name, None)
        if not func:
            raise AttributeError('no attribute: {0}'.format(func_name))
        return func(*query, **kwquery)

    def db(self):
        from pymongo import MongoClient
        db = MongoClient(self.host)
        return db[self.dbname][self.colname]
