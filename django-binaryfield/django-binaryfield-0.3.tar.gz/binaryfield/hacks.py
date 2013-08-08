try:
    from django.utils import six
except ImportError:
    import six

import sys
import django
# from django.core.validators import ValidationError
from django.utils import importlib
from django.utils.functional import Promise

try:
    from django.utils.encoding import force_bytes
except ImportError:

    def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
        """
        Similar to smart_bytes, except that lazy instances are resolved to
        strings, rather than kept as lazy objects.

        If strings_only is True, don't convert (some) non-string-like objects.
        """
        if isinstance(s, six.memoryview):
            s = bytes(s)
        if isinstance(s, bytes):
            if encoding == 'utf-8':
                return s
            else:
                return s.decode('utf-8', errors).encode(encoding, errors)
        if strings_only and (s is None or isinstance(s, int)):
            return s
        if isinstance(s, Promise):
            return six.text_type(s).encode(encoding, errors)
        if not isinstance(s, six.string_types):
            try:
                if six.PY3:
                    return six.text_type(s).encode(encoding)
                else:
                    return bytes(s)
            except UnicodeEncodeError:
                if isinstance(s, Exception):
                    # An Exception subclass containing non-ASCII data that doesn't
                    # know how to print itself properly. We shouldn't raise a
                    # further exception.
                    return b' '.join([force_bytes(arg, encoding, strings_only,
                            errors) for arg in s])
                return six.text_type(s).encode(encoding, errors)
        else:
            return s.encode(encoding, errors)

if hasattr(six, 'memoryview'):
    memoryview = six.memoryview
else:
    if six.PY3 or sys.platform.startswith('java'):
        memoryview = memoryview
    else:
        memoryview = buffer


def hack_engine(engine_module):
    creation = importlib.import_module(engine_module + '.creation')
    byte_type_mapping = {
        'django.db.backends.sqlite3' : 'BLOB',
    }

    creation.DatabaseCreation.data_types['BinaryField'] = byte_type_mapping[engine_module]


def binaryfield_hack_engines(*engine_modules):
    for engine_module in engine_modules:
        hack_engine(engine_module)


def hack_oracle_params(*hack_oracle_param_backends):
    oracle_param_attr_hack_name = ''
    if django.VERSION < (1,5):
        oracle_param_attr_hack_name = 'smart_str'
    elif django.VERSION < (1,6):
        oracle_param_attr_hack_name = 'force_bytes'

    for oracle_backend_engine in hack_oracle_param_backends:
        oracle_base = importlib.import_module(oracle_backend_engine + '.base')
        original_init = oracle_base.OracleParam.__init__

        def paramnewinit(self, param, *args, **kwargs):
            if isinstance(param, memoryview):
                setattr(self, oracle_param_attr_hack_name, param)
                self.input_size = None
            else:
                original_init(self, param, *args, **kwargs)

        paramnewinit._binaryfield_hacked = True

        if not hasattr(oracle_base.OracleParam.__init__, '_binaryfield_hacked'):
            oracle_base.OracleParam.__init__ = paramnewinit
