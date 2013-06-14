from os.path import isdir as _isdir, isfile as _isfile
from dateutil.parser import parse as _parse_date
from unicodedata import normalize as _normalize

from decimal import Decimal
from datetime import date, datetime
from time import time as get_timestamp
from uuid import UUID

from inspect import (
    ismodule as is_module,
    isclass as is_class,
    ismethod as is_method,
    isfunction as is_function,
    isgenerator as is_generator,
)

def is_subclass(term, *args, **argd):
    try:
        return issubclass(term, *args, **argd)
    except:
        return False

def is_lambda(term):
    try:
        return is_function(term) and term.__name__ == is_lambda.__lambda_name__
    except:
        return False
is_lambda.__lambda_name__ = (lambda: None).__name__

def is_file(term):
    try:
        return _isfile(term)
    except:
        return False

def is_dir(term):
    try:
        return _isdir(term)
    except:
        return False

def is_boolean(term):
    return isinstance(term, bool)

def is_uuid(term):
    return isinstance(term, UUID)

def is_date(term):
    return isinstance(term, (date, datetime))

def is_dict(term):
    return isinstance(term, dict) or type(term) == dict

def is_sequence(term):
    return hasattr(term, '__iter__') \
            and not isinstance(term, basestring) \
            and not is_dict(term)

def is_record(term, model = None):
    return isinstance(term, store.Record) \
            and (model is None or term._model == model)

def is_string(term):
    return isinstance(term, basestring)

def is_number(term):
    return isinstance(term, (int, long, float, Decimal))

_record_dump_keys = set(('_model', '_uuid', '_txn', '_vsn', '_time', '_fields'))
def is_record_dump(term):
    return is_dict(term) and set(term.keys()) == _record_dump_keys \
            and term['_model'] in store.models and is_uuid(term['_uuid']) \
            and is_number(term['_vsn']) and is_dict(term['_fields'])

def is_record_ref(term, model = None):
    try:
        rtype, uuid = term
        return is_uuid(uuid) and is_string(rtype) \
                and (model == rtype if model else True) \
                and rtype in store.models
    except:
        return False

def parse_number(term):
    dec = Decimal(term if isinstance(term, basestring) else '%f' % term)
    num = int(dec)
    return num if num == dec else dec.normalize()

def parse_date(term):
    dt = _parse_date(term)
    d = dt.date()
    return d if d == dt else d

def parse_term(term, parse_float = parse_number, seen = None):
    """Transform term to python object."""
    # cache parsed terms (prevent recursion)
    try:
        tid = hash(term)
    except:
        tid = id(term)
    if seen is None:
        seen = dict()
    elif tid in seen:
        return seen[tid]

    if isinstance(term, (int, long, Decimal, hict, UUID, store.Record)) \
       or is_date(term) or is_file(term):
        pass
    elif isinstance(term, float):
        term = parse_float(term)
    elif term and is_string(term):
        try:
            term = parse_float(term)
        except:
            try:
                term = UUID(term)
            except:
                if len(term) > 2:
                    try:
                        term = parse_date(term)
                    except:
                        pass
    elif is_sequence(term):
        term = type(term)(parse_term(i, parse_float, seen) for i in term)
        if is_record_ref(term):
            with store() as db:
                term = db.get(*term)
    elif is_dict(term):
        term = hict()._fill((parse_term(k, parse_float, seen),
                             parse_term(v, parse_float, seen))
                            for k, v in term.items())
        if is_record_dump(term):
            term = store.new(term._model,
                             term._uuid,
                             term._txn,
                             term._vsn,
                             term._time,
                             term._fields)

    try:
        seen[hash(term)] = term
    except:
        seen[id(term)] = term
    seen[tid] = term
    return term

def to_simple(term, seen = None, levels = 1):
    """Transform python object to simple serializable term."""
    # cache transformation (prevent recursion)
    try:
        tid = hash(term)
    except:
        tid = id(term)
    if seen is None:
        seen = dict()
    elif tid in seen:
        return seen[tid]

    if term is None or isinstance(term, (int, long, basestring)):
        pass
    elif isinstance(term, float):
        term = to_simple(parse_number(term), seen, levels)
    elif isinstance(term, store.Record):
        if levels > 0:
            term = to_simple(term.dump(), seen, levels-1)
        else:
            term = (term._model, str(term._uuid))
    elif is_dict(term):
        term = dict((to_simple(k, seen, levels),
                     to_simple(v, seen, levels))
                    for k,v in term.items())
    elif is_sequence(term) or is_generator(term):
        term = list(to_simple(i, seen, levels) for i in term)
    else:
        term = str(term)

    try:
        seen[hash(term)] = term
    except:
        seen[id(term)] = term
    seen[tid] = term
    return term

try:
    from BeautifulSoup import BeautifulSoup as _to_unicode
    def to_str(term, encoding = 'utf8', fromEncoding = None):
        if isinstance(term, unicode):
            return term.encode('utf8')
        else:
            text = term if isinstance(term, str) else str(to_simple(term))
            soup = _to_unicode(text, fromEncoding = fromEncoding)
            return unicode(soup).encode(encoding)
except ImportError:
    def to_str(term, encoding = 'utf8', fromEncoding = None):
        if isinstance(term, unicode):
            return term.encode('utf8')
        elif fromEncoding:
            return text.decode(fromEncoding).encode(encoding)
        else:
            text = term if isinstance(term, str) else str(to_simple(term))
            for e in ('utf8', 'latin1', 'windows-1250', 'windows-1252'):
                try:
                    return text.decode(e).encode(encoding)
                except UnicodeDecodeError, err:
                    continue
            raise err

def to_unicode(text, encoding = 'utf8', fromEncoding = None):
    return to_str(text, encoding, fromEncoding).decode(encoding)

def to_ascii(text, errors = 'ignore', form = 'NFKD'):
    return _normalize(form, text).encode('ascii', errors)

try:
    from cPickle import dumps as _pickle, loads as _unpickle
except ImportError:
    from Pickle import dumps as _pickle, loads as _unpickle
finally:
    def pickle(term):
        return _pickle(to_simple(term))

    def unpickle(term):
        return parse_term(_unpickle(term))

try:
    from yajl import dumps as _to_json, loads as _from_json
except ImportError:
    try:
        from simplejson import dumps as _to_json, loads as _from_json
    except ImportError:
        from json import dumps as _to_json, loads as _from_json
finally:
    def to_json(term):
        return _to_json(to_simple(term))

    def parse_json(term):
        return parse_term(_from_json(term))


class hict(dict):
    """Hierarchycal dotted dictionary with auto-parsing."""

    def __init__(self, *args, **argd):
        if args or argd:
            self.update(*args, **argd)

    def __contains__(self, key):
        return dict.__contains__(self, parse_term(key))

    def __getitem__(self, key):
        k = parse_term(key)
        if not dict.__contains__(self, k):
            return dict.setdefault(self, k, hict())
        else:
            return dict.__getitem__(self, k)

    def __setitem__(self, key, val):
        dict.__setitem__(self, parse_term(key), parse_term(val))

    __getattr__ = __getitem__
    __setattr__ = __setitem__
    __delattr__ = dict.__delitem__

    def _fill(self, *args, **argd):
        if args or argd:
            for k, v in dict(*args, **argd).items():
                dict.__setitem__(self, k, v)
        return self

    def setdefault(self, key, term):
        k = parse_term(key)
        if not dict.__contains__(self, k):
            dict.__setitem__(self, k, parse_term(term))

    def update(self, *args, **argd):
        if args or argd:
            for k, v in dict(*args, **argd).items():
                self[k] = v
        return self

    def merge(self, *args, **argd):
        if args or argd:
            for k, v in dict(*args, **argd).items():
                self.setdefault(k, v)
        return self

    def difference(self, dct):
        return hict((k, v) for k, v in self.items() if k not in dct)

    def union(self, dct):
        return hict(self).update(dct)

    def remove(self, term):
        for key in self.find_keys(term):
            del self[key]
        return self

    def find_keys(self, *args):
        vals = (parse_term(arg) for arg in args)
        for k, v in self.items():
            if v in vals:
                yield k
