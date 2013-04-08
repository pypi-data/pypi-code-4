from contextlib import contextmanager
from copy import copy
from itertools import product, izip, imap, chain
from collections import namedtuple
from json import dumps

import backend
import dimension
import measure

SPACES = {}

class MetaSpace(type):

    def __new__(cls, name, bases, attrs):
        if not '_name' in attrs:
            attrs['_name'] = name

        attrs['_name'] = attrs['_name'].lower()

        for b in bases:
            if not type(b) == cls:
                continue
            if hasattr(b, '_dimensions'):
                for name, dim in b._dimensions:
                    attrs[name] = copy(dim)

            if hasattr(b, '_measures'):
                for name, msr in b._measures:
                    attrs[name] = copy(msr)

        dimensions = []
        measures = []
        for k, v in attrs.iteritems():
            # Collect dimensions
            if isinstance(v, dimension.Dimension):
                dimensions.append((k, v))
                v._name = k

            # Collect measures
            if isinstance(v, measure.Measure):
                measures.append((k, v))
                v._name = k

        attrs['_dimensions'] = dimensions
        attrs['_measures'] = measures
        attrs['_read_cache'] = {}
        attrs['_insert_cache'] = {}
        attrs['_update_cache'] = {}

        spc = super(MetaSpace, cls).__new__(cls, name, bases, attrs)

        for _, dim in dimensions:
            dim._spc = spc

        if bases:
            SPACES[attrs['_name']] = spc

        return spc


class Space:

    __metaclass__ = MetaSpace
    _db = None
    MAX_CACHE = 1000

    @classmethod
    @contextmanager
    def connect(cls, uri):
        cls._db = backend.get_backend(uri)
        for _, dim in cls._dimensions:
            dim.set_db(cls._db)

        for _, msr in cls._measures:
            msr.set_db(cls._db)

        cls._db.register(cls)
        yield
        cls._db.close()

    @classmethod
    def aggregates(cls, point):
        for name, dim in cls._dimensions:
            yield dim.aggregates(point[name])

    @classmethod
    def key(cls, point, create=False):
        return tuple(
            dim.key(point.get(name, dim.default), create=create) \
                for name, dim in cls._dimensions)

    @classmethod
    def load(cls, points):
        for point in points:
            values = tuple(point[m] for m, _ in cls._measures)
            for parent_coords in product(*tuple(cls.aggregates(point))):
                cls._db.increment(parent_coords, values)

    @classmethod
    def fetchmany(cls, points):
        keys = (cls.key(p, False) for p in points)
        return cls._db.fetch(keys)

    @classmethod
    def fetch(cls, **point):
        keys = (cls.key(point, False),)
        return cls._db.fetch(keys).next()

    @classmethod
    def dice(cls, point):
        points = list(cls.drill(point))
        for point, res in izip(points, cls.fetchmany(points)):
            point.update(res)
            yield point

    @classmethod
    def drill(cls, point):
        res = {}
        vals = []
        for name, dim in cls._dimensions:
            if name not in point:
                continue
            vals.append(dim.explode(point[name]))

        for point_tuple in product(*vals):
            sub_point = {}
            pos = 0
            for name, dim in cls._dimensions:
                if name not in point:
                    continue
                sub_point[name] = point_tuple[pos]
                pos += 1
            yield sub_point


def build_space(data_point, name):
    """
    Dynamically create a Space class based on a data point.
    """

    attributes = {}
    for k, v in data_point.iteritems():
        if isinstance(v, list):
            col_type = "integer"
            if isinstance(v[0], basestring):
                col_type = 'varchar'
            attributes[k] = dimension.Tree(k, type=col_type)
        elif isinstance(v, (int, float)):
            attributes[k] = measure.Sum(k)
        else:
            raise Exception('Unknow type %s (on key %s)' % (type(v), k))

    return type(name, (Space,), attributes)
