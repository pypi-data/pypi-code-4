from collections import defaultdict
from django.db import models
import cPickle
import numpy as np
import ast

class TagField(models.TextField):
    description = "Stores tags in a single database column."
    __metaclass__ = models.SubfieldBase

    def __init__(self, delimiter="|", *args, **kwargs):
        self.delimiter = delimiter
        super(TagField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if not value:
            return []
        # Otherwise, split by delimiter
        return value.split(self.delimiter)

    def get_prep_value(self, value):
        return self.delimiter.join(value)

class NumpyArrayField(models.TextField):
    description = "Stores a Numpy ndarray."
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(NumpyArrayField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, list):
            value = np.array(list)
        if isinstance(value, np.ndarray):
            return value

        if not value:
            return np.array([])
        return np.array(cPickle.loads(str(value)))

    def get_prep_value(self, value):
        if isinstance(value, list):
            return cPickle.dumps(value)
        elif isinstance(value, np.ndarray):
            return cPickle.dumps(value.tolist())
        else:
            raise TypeError('%s is not a list or numpy array' % value)

class DictField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python dictionary"

    def __init__(self, *args, **kwargs):
        super(DictField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = {}

        if isinstance(value, dict):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        if isinstance(value, defaultdict):
            value = dict(value)

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class DictModel(models.Model):
    data = DictField(max_length=255, primary_key=True)

    class Meta:
        abstract = True

    ## dict methods
    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

