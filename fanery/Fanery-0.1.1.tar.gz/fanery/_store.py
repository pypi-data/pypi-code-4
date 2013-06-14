from contextlib import contextmanager
from weakref import WeakValueDictionary

from fanery.terms import (
    parse_term, hict, get_timestamp, is_record_dump,
    is_class, is_string, is_date, is_number, is_boolean,
    is_uuid, is_sequence, is_record, is_record_ref,
    is_lambda, is_dict, is_file,
)
from fanery.crypto import digest, gen_token
from fanery.librand import randuuid
from fanery import service

class store(object):

    class MultipleRecordsFound(AssertionError):
        pass

    class NoResult(AssertionError):
        pass

    class DuplicatedKey(AssertionError):
        pass

    class ValidationError(AssertionError):
        pass

    class VersioningMismatch(AssertionError):
        pass

    _default_field_meta_definition = dict(
        # default setter/getter
        fget = lambda term, rec: (True, term),
        fset = lambda term, rec, old: (True, term),
        finit = None, # default to fset
        fdel = lambda term, rec: True,
        # auto parse term on set by default
        auto_parse = True,
        # use me as 2nd arg during validation
        use_on_validate = False,
        # default constaints
        validators = [],
        not_null = False,
        is_write_only = False,
        is_read_only = False,
        is_required = False,
        is_unique = False,
        is_key = False,
        # callable for transient fields
        fcomp = None)

    class data:

        class Term(dict):

            __getattr__ = dict.__getitem__
            __setattr__ = dict.__setitem__

            def __init__(self, basetype, **argd):
                assert isinstance(basetype, str)
                argd.update(basetype = basetype)
                is_unique = argd.setdefault('is_unique', False)
                is_required = argd.setdefault('is_required', is_unique)
                argd.setdefault('not_null', is_required)
                argd['validators'] = tuple(argd.setdefault('validators', []))
                argd.setdefault('use_on_validate', False)
                dict.__init__(self, **argd)

            def __call__(self, **argd):
                term = self.__class__(**self) # clone myself
                term.validators += tuple(argd.pop('validators', []))
                is_unique = argd.setdefault('is_unique', term.is_unique)
                is_required = argd.setdefault('is_required', is_unique or term.is_required)
                argd.setdefault('not_null', is_required or term.not_null)
                term.update(argd)
                return term

        Link = Term('Link', use_on_validate = True,
                fget = lambda term, rec: (True, parse_term(term)),
                validators = [lambda term, meta: is_record(term, meta.model) or 'bad-type'])

        Links = Term('Links', use_on_validate = True,
                fget = lambda term, rec: (True, parse_term(term)),
                validators = [lambda terms, meta: all(is_record(t, meta.model) for t in terms) or 'bad-type'])

        Boolean = Term('Boolean', validators = [is_boolean])

        Number = Term('Number', validators = [is_number])

        UUID = Term('UUID', validators = [is_uuid])

        Date = Term('Date', validators = [is_date])

        Dict = Term('Dict', validators = [is_dict])

        File = Term('File', validators = [is_file])

        List = Term('List', validators = [is_sequence])

        String = Term('String', validators = [is_string])

        Timestamp = Term('Timestamp', read_only = True, is_required = True,
                default = get_timestamp, validators = [is_number])

        NotEmptyString = String(not_null = True, validators = [lambda term: bool(term.strip()) or 'empty'])

        NotEmptyAlpha = NotEmptyString(validators = [lambda term: term.isalnum()])

        UniqueString = NotEmptyString(is_unique = True)

        UniqueAlpha = NotEmptyAlpha(is_unique = True)

        Password = NotEmptyString(is_required = True,
            fset = lambda term, rec, _: (True, digest(term)),
            validators = [lambda term: not term.isalnum() or 'too-simple',
                          lambda term: len(term) > 8 or 'too-short'])

    class Record(object):

        def __str__(self):
            return '<Record %s uuid: %s vsn: %s>' % (
                self._model, self._uuid, self._vsn)
        __repr__ = __str__

        def __getattr__(self, attr):
            if attr[0] == '_':
                raise AttributeError("'%s' record has no attribute '%s'" % (
                    self._model, attr))
            meta = self._meta_[attr]
            if not meta:
                meta._fill(store._default_field_meta_definition)
            elif meta.write_only:
                raise store.ValidationError('write-only', attr)
            elif meta.fcomp:
                return meta.fcomp(self)
            fields = self._fields
            if attr in fields:
                doit, term = meta.fget(fields[attr], self)
                if not doit:
                    raise store.ValidationError('write-only', attr)
                return term
            elif 'default' in meta:
                default = meta.default
                term = default() if callable(default) else default
                return fields.setdefault(attr, term)
            else:
                raise AttributeError("'%s' record attribute '%s' is unset %r" % (
                    self._model, attr, meta))

        def __setattr__(self, attr, term):
            if attr.startswith('_'):
                self.__dict__[attr] = term
            else:
                meta = self._meta_[attr]
                if not meta:
                    meta._fill(store._default_field_meta_definition)
                fields = self._fields
                if meta.read_only and attr in fields and fields[attr] != term:
                    raise store.ValidationError('read-only', attr)
                elif meta.fcomp:
                    raise store.ValidationError('transient', attr)
                elif meta.not_null and term is None:
                    raise store.ValidationError('not-null', attr)
                elif term is not None:
                    if meta.auto_parse:
                        term = parse_term(term)
                    for validator in meta.validators:
                        if meta.use_on_validate:
                            match = validator(term, meta)
                        else:
                            match = validator(term)
                        if match is not True:
                            raise store.ValidationError(match or (
                                'invalid' if is_lambda(validator) \
                                        else validator.__name__.replace('_','-')),
                                attr)
                if attr in fields:
                    doit, term = meta.fset(term, self, fields[attr])
                elif not callable(meta.finit):
                    doit, term = meta.fset(term, self, None)
                else:
                    doit, term = meta.finit(term, self)
                if not doit:
                    raise store.ValidationError('read-only', attr)
                fields[attr] = term

        def __delattr__(self, attr):
            meta = self._meta_[attr]
            if meta.fcomp:
                raise store.ValidationError('transient', attr)
            if meta.fdel(attr, self) is True:
                del self._fields[attr]

        def dump(self):
            return hict((k,v) for k,v in self.__dict__.items()
                        if k[0] == '_' and not k[-1] == '_')

        def load(self, dump):
            self.__dict__.update((k,v) for k,v in dump.items()
                    if k[0] == '_' and not k[-1] == '_')
            return self

    def __init__(self):
        self.models = dict()
        self.cache = dict()
        self.meta = hict()
        self.dbms = set()

    def set_definition(self, model, **argd):
        # extract/update fields definitions
        fields = dict((k, hict()._fill(v).merge(self._default_field_meta_definition))
                      for k,v in argd.items()
                      if isinstance(v, store.data.Term))
        # update model meta definition
        self.meta[model].merge(validators = [])\
            ._fill((k, argd[k]) for k in argd if k not in fields)\
            ._fill(unique = tuple(k for k in fields if fields[k].is_unique),
                   key = tuple(k for k in fields if fields[k].is_key),
                   fields = hict()._fill(fields))

    def join(self, dbm, *models):
        self.dbms.add(dbm)
        for model in models:
            self.models[model] = dbm.model(model)
            self.meta[model].merge(validators = [])
            self.cache[model] = WeakValueDictionary()

    @contextmanager
    def __call__(self):
        state = service.state
        if state.txn:
            yield self
        else:
            txn = state.txn = gen_token()
            dbms = self.dbms
            try:
                for dbm in dbms:
                    dbm.begin(txn)
                yield self
                for dbm in dbms:
                    dbm.prepare_commit(txn)
                for dbm in dbms:
                    dbm.commit(txn)
            except:
                for dbm in dbms:
                    dbm.rollback(txn)
                raise
            finally:
                state.txn = None

    def validate(self, record):
        meta = self.meta[record._model]
        # fields validators
        for field, f_meta in meta.fields.items():
            if f_meta.is_required \
                    and field not in record._fields \
                    and 'default' not in f_meta:
                raise store.ValidationError('required', field)
            try:
                fval = getattr(record, field)
            except:
                continue # unset but not required
            if fval is not None:
                for validator in f_meta.validators:
                    if f_meta.use_on_validate:
                        match = validator(fval, f_meta)
                    else:
                        match = validator(fval)
                    if match is not True:
                        raise store.ValidationError(match or (
                            'invalid' if is_lambda(validator) \
                                    else validator.__name__.replace('_','-')),
                            field, fval)
            elif f_meta.not_null:
                raise store.ValidationError('not-null', field)
        # record validators
        for validator in meta.validators:
            validator(record)
        # then check fields uniqueness
        fetch = self.models[record._model].fetch
        if meta.unique:
            for field in meta.unique:
                try:
                    fval = getattr(record, field)
                except:
                    continue # don't care for uniqueness if unset
                query = {field: getattr(record, field)}
                stored = fetch(**query)
                if stored and stored._uuid != record._uuid:
                    raise store.DuplicatedKey(query)
        # and finally check composite key uniqueness
        if meta.key:
            query = dict((field, getattr(record, field, None)) for field in meta.key)
            stored = fetch(**query)
            if stored and stored._uuid != record._uuid:
                raise store.DuplicatedKey(query)

    def new(self, model, *meta, **fields):
        record = store.Record()
        lmeta = len(meta)
        record.__dict__.update(
            _meta_ = self.meta[model].fields,
            _model = model,
            _uuid = meta[0] if lmeta else randuuid(),
            _txn = meta[1] if lmeta > 1 else None,
            _vsn = meta[2] if lmeta > 2 else 0,
            _time = meta[3] if lmeta > 3 else 0,
            _fields = meta[4] if lmeta > 4 else fields)
        return self.cache[model].setdefault((record._uuid, record._vsn), record)

    def _ret(self, ret, fail, model, *args):
        if ret:
            return self.cache[model].setdefault((ret._uuid, ret._vsn), ret)
        elif is_class(fail) and issubclass(fail, Exception):
            raise fail(model, *args)
        elif callable(fail):
            return fail()
        else:
            return fail

    def get(self, model, uuid, fail = NoResult):
        return self._ret(self.models[model].get(uuid), fail, model, uuid)

    def fetch(self, model, fail = NoResult, **argd):
        return self._ret(self.models[model].fetch(**argd), fail, model, argd)

    def select(self, model, **argd):
        cache = self.cache[model]
        for rec in self.models[model].select(**argd):
            yield cache.setdefault((rec._uuid, rec._vsn), rec)

    def insert(self, record_or_model, **argd):
        record = record_or_model if isinstance(record_or_model, store.Record) \
                 else self.new(record_or_model)
        for field, value in argd.items():
            if not field.startswith('_'):
                setattr(record, field, value)
        self.validate(record)
        record._vsn = 1
        record._txn = service.state.txn
        record._time = get_timestamp()
        self.models[record._model].insert(record)
        return self.cache[record._model].setdefault((record._uuid, 1), record)

    def update(self, record):
        assert record is self.cache[record._model][(record._uuid, record._vsn)]
        self.validate(record)
        record._vsn += 1
        record._txn = service.state.txn
        record._time = get_timestamp()
        self.models[record._model].update(record)
        return record

    def delete(self, record):
        key = (record._uuid, record._vsn)
        model = record._model
        cache = self.cache[model]
        assert record is cache[key]
        record._vsn *= -1
        record._txn = service.state.txn
        record._time = get_timestamp()
        self.models[model].delete(record)
        del cache[key]

    def clear(self, model):
        self.models[model].clear()
        self.cache[model].clear()

    def clearAll(self):
        cache = self.cache
        models = self.models
        for model in models:
            models[model].clear()
            cache[model].clear()
