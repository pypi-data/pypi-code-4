from fanery.terms import parse_term
from fanery import store

class Model(object):

    def __init__(self, name, db):
        self.name = name
        self.records = db.records.setdefault(name, dict())

    def get(self, uuid):
        return self.records.get(uuid, None)

    def fetch(self, **argd):
        record = None
        for idx, record in enumerate(self.select(**argd)):
            if idx > 0:
                raise store.MultipleRecordsFound()
        return record

    def select(self, **argd):
        query = parse_term(argd).items()
        for record in self.records.values():
            fields = record.dump()._fields
            for k, v in query:
                if k not in fields or fields[k] != v:
                    break
            else:
                yield record

    def store(self, record):
        self.records[record._uuid] = record
    insert = update = store

    def delete(self, record):
        del self.records[record._uuid]

    def clear(self):
        self.records.clear()

class SimpleMemoryDB(object):

    def __init__(self):
        self.records = dict()

    def begin(self, txn):
        pass

    def prepare_commit(self, txn):
        pass

    def commit(self, txn):
        pass

    def rollback(self, txn):
        pass

    def model(self, name):
        return Model(name, self)
