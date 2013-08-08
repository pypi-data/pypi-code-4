# from django.db import models
from base64 import b64decode, b64encode
from django.db.models.fields import Field
from binaryfield.hacks import six, memoryview, binaryfield_hack_engines, hack_oracle_params, force_bytes
from django.core import validators
from django.utils import importlib
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import django
# Create your models here.


class BinaryField(Field):
    description = _("Raw binary data")
    empty_values = [None, b'']

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(BinaryField, self).__init__(*args, **kwargs)
        if self.max_length is not None:
            self.validators.append(validators.MaxLengthValidator(self.max_length))

    def get_internal_type(self):
        return "BinaryField"

    def get_default(self):
        if self.has_default() and not callable(self.default):
            return self.default
        default = super(BinaryField, self).get_default()
        if default == '':
            return b''
        return default

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(BinaryField, self).get_db_prep_value(value, connection, prepared)
        # import pdb; pdb.set_trace()
        if value is not None:
            base = importlib.import_module(connection.__module__)
            return base.Database.Binary(value)
        return value

    def value_to_string(self, obj):
        """Binary data is serialized as base64"""
        return b64encode(force_bytes(self._get_val_from_obj(obj))).decode('ascii')

    def to_python(self, value):
        # If it's a string, it should be base64-encoded data
        if isinstance(value, six.text_type):
            return memoryview(b64decode(force_bytes(value)))
        return value


HACK_ENGINES = getattr(settings, 'BINARYFIELD_HACK_ENGINES', None)

if HACK_ENGINES is not None and django.VERSION < (1, 6):
    binaryfield_hack_engines(*HACK_ENGINES)


# Oracle needs a different OracleParam handling see: https://github.com/django/django/blob/1.6b1/django/db/backends/oracle/base.py#L689
HACK_ORACLE_PARAM = getattr(settings, 'BINARYFIELD_HACK_ORACLE_PARAM', False)
HACK_ORACLE_PARAM_BACKENDS = getattr(settings, 'BINARYFIELD_HACK_ORACLE_PARAM_BACKENDS', [ settings.DATABASES['default']['ENGINE'] ])

if HACK_ORACLE_PARAM and django.VERSION < (1, 6):
    hack_oracle_params(*HACK_ORACLE_PARAM_BACKENDS)
