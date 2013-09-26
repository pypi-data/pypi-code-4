"""
Storage proxy, not an ORM.
"""
__all__ = ['add_storage', 'add_model', 'Aict', 'Record', 'storage']

from _term import to_simple, parse_term, gen_uuid

storage_reg = dict()
model_reg = dict()

def add_storage(storage, *models):
    for model in models:
        assert model in model_reg, ('unknown-model', model)
        storage_reg[model] = storage
        storage.add_model(model, get_indexer(model))

def add_model(model, validator = None, initializer = None, indexer = None):
    model_reg[model] = (validator, initializer, indexer)

def get_storage(model):
    assert model in storage_reg, model
    return storage_reg[model]

def get_validator(model):
    return model_reg[model][0] if model in model_reg else None

def get_initializer(model):
    return model_reg[model][1] if model in model_reg else None

def get_indexer(model):
    return model_reg[model][2] if model in model_reg else None

class Aict(dict):
    """
    Hierarchical dotted dictionary with value auto-parsing.
    """

    def __missing__(self, key):
        term = self[key] = Aict()
        return term

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, parse_term(value, dct=Aict))

    __setattr__ = __setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__

class Record(object):

    def __init__(self, model, uuid, vsn, txn = None, _dct_ = None, **dct):
        store = get_storage(model)
        if _dct_:
            self._dct = parse_term(_dct_, dct=Aict)
        elif dct:
            self._dct = parse_term(dct, dct=Aict)
        else:
            record_data = store.get(uuid, txn, vsn, txn)
            assert record_data, 'not-found: %s %s' % (model, uuid)
            uuid, vsn, txn, data = record_data
            self._dct = parse_term(data, dct=Aict)
        self._mark = 0 # 1 -> insert, 2 -> update, 3 -> delete
        self._store = store
        self._model = model
        self._uuid = parse_term(uuid)
        self._vsn = parse_term(vsn)
        self._txn = parse_term(txn)
        initialize = get_initializer(model)
        if initialize:
            initialize(self)

    def __getattr__(self, key):
        return self._dct[key]

    def __setattr__(self, key, value):
        dct = self.__dict__ if key[0] == '_' else self._dct
        dct[key] = parse_term(value, dct=Aict)

    def __delattr__(self, key):
        if key[0] != '_':
            del self._dct[key]

    def update(self, *args, **argd):
        self._dct.update(*args if args else argd)
        return self

    def merge(self, *args, **argd):
        dct = self._dct
        dct.update((k, v) for k, v in (args or argd.iteritems()) if k not in dct)
        return self

class storage(object):

    def __init__(self):
        self._cache = dict()
        self._txn = gen_uuid()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self._cache:
            if isinstance(value, Exception):
                self.__rollback()
            else:
                self.__commit()

    def __commit(self):
        dirty, dbms = set(), set()
        for (model, uuid, vsn), record in self._cache.iteritems():
            if record._mark:
                store = record._store
                if store.transactional is True:
                    dbms.add(store)
                dirty.add(record)
        try:
            txn = self._txn
            for dbm in dbms:
                dbm.begin_transaction(txn)
            for record in dirty:
                mark = record._mark
                try:
                    _vsn, _txn = record._vsn, record._txn
                    if mark == 1:
                        record._vsn = 1
                        record._store.insert(txn, record)
                    elif mark == 2:
                        record._vsn += 1
                        record._store.update(txn, record)
                    elif mark == 3:
                        record._vsn *= -1
                        record._store.delete(txn, record)
                    record._txn = txn
                    record._mark = 0
                except:
                    record._vsn, record._txn = _vsn, _txn
                    raise
            for dbm in dbms:
                dbm.commit(txn)
        except:
            self.__rollback()

    def __rollback(self):
        txn, dbms = self._txn, set()
        for record in self._cache.itervalues():
            if record._mark:
                store = record._store
                if store.transactional is True:
                    dbms.add(store)
        for dbm in dbms:
            dbm.rollback(txn)

    def fetch(self, model, uuid, vsn = None, txn = None, acl = None, fail = None):
        cache = self._cache
        record = cache.get((model, uuid, vsn), None)
        if record and record._mark == 3:
            record = None
        elif record is None:
            storage = get_storage(model)
            term = storage.fetch(model, uuid, vsn, txn)
            record = term if isintance(Record, term) else Record(model, uuid, *term)
            cache[(model, uuid, record._vsn)] = record

        if record and acl and acl(record) is not True:
            record = None

        if record:
            return record
        elif issubclass(fail, Exception):
            raise fail
        elif callable(fail):
            return fail()
        else:
            return fail

    def query(self, method, model, fun, acl = None, raw = False, load = parse_term):
        index = get_storage(model)
        cache = self._cache

        for term in getattr(index, method)(model, fun):
            if raw is True:
                yield load(term) if load else term

            if len(term) == 4:
                uuid, vsn, txn, score = term
            else:
                uuid, vsn, txn = term
                score = None
            record = cache.get((model, uuid, vsn), None)

            if record is None:
                record = self.fetch(model, uuid, vsn, txn, acl)
                if record is None:
                    continue
                cache[(model, uuid, vsn)] = record
            elif record._mark == 3 or (acl and acl(record) is not True):
                continue
            yield (score, record) if score is not None else record

    def search(self, model, fun, acl = None):
        return self.query('search', model, fun, acl)

    def select(self, model, fun, acl = None):
        return self.query('select', model, fun, acl)

    def select_one(self, model, fun, acl = None):
        record = None
        for idx, record in enumerate(self.select(model, fun, acl)):
            assert idx == 0, 'multiple-results'
        return record

    def insert(self, model, *args, **argd):
        uuid, vsn = gen_uuid(), 0
        record = Record(model, uuid, vsn, self._txn, *args, **argd)
        self.validate(record)
        record._mark = 1
        return self._cache.setdefault((model, uuid, vsn), record)

    def update(self, *records):
        for record in records:
            mark = record._mark
            assert mark != 3 and record._vsn >= 0, record
            self.validate(record)
            if mark == 0:
                record._mark = 2

    def delete(self, *records):
        for record in records:
            assert record._mark != 1 and record._vsn > 0, record
            record._mark = 3

    def validate(self, record):
        validator = get_validator(record._model)
        if validator:
            errors = validator(record)
            assert not errors, (record, errors)
