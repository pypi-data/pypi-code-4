from copy import deepcopy
from django.db import models
from django.db.models import Q, Count, Sum, Avg, Max, Min, StdDev, Variance
from django.db.models.query import REPR_OUTPUT_SIZE
from django.db.models.sql.constants import LOOKUP_SEP
from modeltree.utils import M


class Aggregator(object):
    def __init__(self, field, model=None):
        if not isinstance(field, models.Field):
            if not model:
                raise TypeError('Field instance or field name and model class required')
            field_name = field
            field = model._meta.get_field_by_name(field_name)[0]
        else:
            model = field.model
            field_name = field.name

        self.field = field
        self.field_name = field_name
        self.model = model

        self._queryset = None
        self._aggregates = {}
        self._filter = []
        self._exclude = []
        self._having = []
        self._groupby = []
        self._orderby = []

    def __eq__(self, other):
        return list(self) == other

    def __deepcopy__(self):
        return self._clone()

    def __len__(self):
        # If the result cache is filled, use the length otherwise
        # performa databse hit
        if hasattr(self, '_length'):
            return self._length
        return len(self._construct())

    def __repr__(self):
        data = list(self[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = '...(remaining elements results)...'
        return repr(data)

    def __getitem__(self, key):
        return list(self._result_iter())[key]

    def __iter__(self):
        return self._result_iter()

    def _result_iter(self):
        if hasattr(self, '_result_cache'):
            for obj in self._result_cache:
                yield obj
        else:
            queryset = self._construct()
            cache = []
            length = 0

            for obj in iter(queryset):
                if self._groupby:
                    keys = []
                    for key in self._groupby:
                        keys.append(obj[key])
                        del obj[key]
                    obj['values'] = keys

                length += 1
                cache.append(obj)
                yield obj

            self._result_cache = cache
            self._length = length

    def _construct(self):
        if self._queryset is None:
            queryset = self.model.objects.all()
        else:
            queryset = self._queryset
        if self._filter:
            queryset = queryset.filter(*self._filter)
        if self._exclude:
            queryset = queryset.exclude(*self._exclude)
        if self._groupby:
            queryset = queryset.values(*self._groupby)
        if self._aggregates:
            if self._groupby:
                queryset = queryset.annotate(**self._aggregates)
            else:
                queryset = queryset.aggregate(**self._aggregates)
        if self._having:
            queryset = queryset.filter(*self._having)
        if self._orderby:
            queryset = queryset.order_by(*self._orderby)
        if not self._groupby:
            return [dict(queryset)]
        return queryset

    def _clone(self):
        clone = self.__class__(self.field_name, self.model)
        clone._aggregates = deepcopy(self._aggregates)
        clone._filter = deepcopy(self._filter)
        clone._exclude = deepcopy(self._exclude)
        clone._having = deepcopy(self._having)
        clone._groupby = deepcopy(self._groupby)
        clone._orderby = deepcopy(self._orderby)
        clone._queryset = self._queryset
        return clone

    def _aggregate(self, *groupby, **aggregates):
        clone = self._clone()
        clone._aggregates.update(aggregates)
        if groupby:
            clone._groupby = groupby
        return clone

    def apply(self, queryset):
        clone = self._clone()
        clone._queryset = queryset
        return clone

    def filter(self, *values, **filters):
        clone = self._clone()

        raw = []
        args = []
        for v in values:
            if isinstance(v, Q):
                args.append(v)
            else:
                raw.append(v)

        # One or more values allowed values for the applied to this
        # data field. This is currently restricted to an `exact` or `in`
        # operator.
        if raw:
            if len(raw) == 1:
                condition = clone.field_name, raw[0]
            else:
                condition = u'{0}__in'.format(clone.field_name), raw
            clone._filter.append(M(tree=clone.model, **dict([condition])))

        clone._filter.extend(args)

        # Separate out the conditions that apply to aggregations. The
        # non-aggregation conditions will always be applied before the
        # aggregation is applied.
        for key, value in filters.iteritems():
            if key.split(LOOKUP_SEP)[0] in clone._aggregates:
                condition = Q(**dict([(key, value)]))
                clone._having.append(condition)
            else:
                condition = M(tree=clone.model, **dict([(key, value)]))
                clone._filter.append(condition)
        return clone

    def exclude(self, *values, **filters):
        clone = self._clone()

        raw = []
        args = []
        for v in values:
            if isinstance(v, Q):
                args.append(v)
            else:
                raw.append(v)

        # One or more values allowed values for the applied to this
        # data field. This is currently restricted to an `exact` or `in`
        # operator.
        if raw:
            if len(raw) == 1:
                condition = clone.field_name, raw[0]
            else:
                condition = u'{0}__in'.format(clone.field_name), raw
            clone._exclude.append(M(tree=clone.model, **dict([condition])))

        clone._exclude.extend(args)

        # Separate out the conditions that apply to aggregations. The
        # non-aggregation conditions will always be applied before the
        # aggregation is applied.
        for key, value in filters.iteritems():
            if key.split(LOOKUP_SEP)[0] in clone._aggregates:
                condition = ~Q(**dict([(key, value)]))
                clone._having.append(condition)
            else:
                condition = ~M(tree=clone.model, **dict([(key, value)]))
                clone._exclude.append(condition)
        return clone

    def order_by(self, *fields):
        clone = self._clone()
        orderby = []
        for f in fields:
            direction = ''
            if f.startswith('-'):
                f = f[1:]
                direction = '-'
            orderby.append(direction + f)
        clone._orderby = orderby
        return clone

    def groupby(self, *groupby):
        clone = self._aggregate(*groupby)
        return clone

    def count(self, *groupby, **kwargs):
        "Performs a COUNT aggregation."
        distinct = kwargs.get('distinct', False)
        if distinct:
            aggregates = {'distinct_count': Count(self.field_name,
                distinct=distinct)}
        else:
            aggregates = {'count': Count(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def sum(self, *groupby):
        "Performs an SUM aggregation."
        aggregates = {'sum': Sum(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def avg(self, *groupby):
        "Performs an AVG aggregation."
        aggregates = {'avg': Avg(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def min(self, *groupby):
        "Performs an MIN aggregation."
        aggregates = {'min': Min(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def max(self, *groupby):
        "Performs an MAX aggregation."
        aggregates = {'max': Max(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def stddev(self, *groupby):
        "Performs an STDDEV aggregation."
        aggregates = {'stddev': StdDev(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def variance(self, *groupby):
        "Performs an VARIANCE aggregation."
        aggregates = {'variance': Variance(self.field_name)}
        return self._aggregate(*groupby, **aggregates)
