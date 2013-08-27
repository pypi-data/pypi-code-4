from django.db import models
from db_defaults.settings import DB_DEFAULTS_ENABLE_ALL_MODELS, DB_DEFAULTS_ENABLE_ALL_FIELDS

class DefaultProxyField(object):
    def __init__(self, field, default=None, db = None, **kwargs):
        """
        Set db default value to
            1. Custom provided value
            2. Otherwise, auto computed default if field_defaults_enabled=True and
               field default is not callable.
        We ignore callable default values as of now as they might generate unexpected default values
        """

        self.field = field
        field_defaults_enabled = DB_DEFAULTS_ENABLE_ALL_MODELS or DB_DEFAULTS_ENABLE_ALL_FIELDS

        self.default = default
        self.escape_default = True
        if self.default is None and field_defaults_enabled and self.field.has_default() \
            and not callable(self.field.default):
            self.default = self.field.get_default()

        #set default if its a datetime field with auto_now
        if self.default is None:
            if isinstance(self.field, models.DateTimeField):
                self.escape_default = False
                self.default = db.get_db_transform("current_timestamp")
            elif isinstance(self.field, models.DateField):
                self.escape_default = False
                self.default = db.get_db_transform("current_date")

    def __getattr__(self, name):
        return getattr(self.field, name)

    def get_default(self):
        return self.default

    def has_default(self):
        return (self.default is not None)

    def is_default_escaped(self):
        return (self.escape_default)

    def has_alters(self):
        return self.has_default()