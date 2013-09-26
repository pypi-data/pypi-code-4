from inspect import ismodule as is_module, \
                    isfunction as is_function, \
                    isgenerator as is_generator, \
                    isbuiltin as is_builtin, \
                    isclass as is_class

from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

class Hict(dict):
    """
    Hierarchical dotted dictionary.
    """

    def __missing__(self, key):
        term = self[key] = Hict()
        return term

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def is_str(term):
    return isinstance(term, basestring)

def is_number(term):
    return isinstance(term, (int, float, Decimal))

def is_date(term):
    return isinstance(term, (date, datetime))

def is_uuid(term):
    return isinstance(term, UUID)

def is_sequence(term):
    return hasattr(term, '__iter__') and \
            not isinstance(term, (basestring, dict))

def is_dict(term):
    return isinstance(term, dict) or type(term) is dict

def is_inet_address(term):
    raise NotImplementedError

def is_inet6_address(term):
    raise NotImplementedError

def is_file(term):
    raise NotImplementedError

def is_dir(term):
    raise NotImplementedError

from re import compile as regex

from uuid import uuid4 as gen_uuid

try:
    from validate_email import validate_email as is_email
except ImportError:
    from email.utils import parseaddr as _parse_email_addr
    # borrowed from http://www.regular-expressions.info/email.html
    _email_regex = regex(r'''[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?''')
    def is_email(term, verify = False):
        try:
            name, email = _parse_email_addr(term)
            return _email_regex.match(email)
        except:
            return False

def to_str(term):
    #FIXME: handle any term
    return '%s' % term

def to_simple(term):
    if not term or isinstance(term, (int, float, basestring)):
        return term
    elif isinstance(term, dict) or type(term) is dict:
        return dict((to_simple(k), to_simple(v))
                    for k, v in term.iteritems())
    elif hasattr(term, '__iter__'):
        return [to_simple(t) for t in term]
    else:
        return str(term)

def parse_term(term, dct=dict):
    if not term:
        return term
    elif isinstance(term, basestring):
        try:
            f = float(term)
            i = int(f)
            if i == f:
                return i
            elif str(f) == term:
                return f
            else:
                return Decimal(term)
        except:
            pass
        try:
            return UUID(term)
        except:
            pass
        if len(term.strip()) >= 3:
            try:
                return parse_date(term)
            except:
                pass
        return term
    elif isinstance(term, dict) or type(term) is dict:
        return dct((parse_term(k, dct), parse_term(v, dct))
                    for k, v in term.iteritems())
    elif hasattr(term, '__iter__'):
        return type(term)(parse_term(t, dct) for t in term)
    else:
        return term

try:
    from dateutil.parser import parse as parse_date
except:
    raise #FIXME: multiple modules or simple default implementation

try:
    from ujson import dumps as to_json, \
                      loads as parse_json
except ImportError:
    try:
        from yajl import Encoder, Decoder
        parse_json = Decoder().decode
        to_json = Encoder().encode
    except ImportError:
        try:
            from jsonlib import write as to_json, \
                                read as parse_json
        except ImportError:
            try:
                from cjson import encode as to_json, \
                                  decode as parse_json
            except ImportError:
                try:
                    from simplejson import dumps as to_json, \
                                           loads as parse_json
                except ImportError:
                    from json import dumps as to_json, \
                                     loads as parse_json

from unicodedata import normalize as _normalize
_punct_regex = regex(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

def normalize(term, mode = 'NFKD'):
    assert isinstance(term, basestring), 'bad-type: %r' % term
    text = ' '.join(_punct_regex.split(text))
    return _normalize(mode, text).encode('ascii', 'ignore')

def slugify(term, delim = '-'):
    return normalize(term).lower().replace(' ', delim)
