# -*- coding: utf-8 -*- 
from __future__ import unicode_literals

import six

from rest_framework.filters import BaseFilterBackend

from nodetree.exceptions import QueryParamError

try:
    import microfilters
except ImportError:
    microfilters = None


FilterSet = microfilters and microfilters.FilterSet or None
Filter = microfilters and microfilters.Filter or None

if microfilters:
    class NodeTypeFilter(Filter):

        def sanitize(self, value):
            if not isinstance(value, six.text_type):
                raise QueryParamError
            node_type_list = value.split(',')
            return list(filter(lambda x: value != '', node_type_list))

        def filter(self, queryset, value):
            return queryset.filter(node_type__in=value)


    class LevelFilter(Filter):

        def sanitize(self, value):
            try:
                value = int(value)
            except Exception:
                value = -1
            if value < 0:
                raise QueryParamError
            return value


    class FromLevelFilter(LevelFilter):

        def filter(self, queryset, value):
            return queryset.filter(level__gte=value)


    class ToLevelFilter(LevelFilter):

        def filter(self, queryset, value):
            return queryset.filter(level__lte=value)


    class NodeFilterSet(FilterSet):

        def sanitize(self, query_dict):
            return dict((k, v) for k, v in six.iteritems(query_dict) if (v == n for n in six.iterkeys(self._filters)))

        def __init__(self):
            super(NodeFilterSet, self).__init__({
                'node_type': NodeTypeFilter(),
                'from_level': FromLevelFilter(),
                'to_level': ToLevelFilter()
            })


class MicrofiltersFilterBackend(BaseFilterBackend):

    """
    A filter backend that uses microfilters.
    """

    def __init__(self):
        assert microfilters, 'Using MicrofiltersFilterBackend, but microfilters is not installed'

    def get_filter_set(self, view):

        filter_set = getattr(view, 'filter_set', None)
        return filter_set

    def filter_queryset(self, request, queryset, view):
        filter_set = self.get_filter_set(view)

        if filter_set:
            query_dict = filter_set.sanitize(request.QUERY_PARAMS)
            return filter_set.filter(queryset, query_dict)
        return queryset


if microfilters:
    node_filter_set = NodeFilterSet()
    node_filter_backend = MicrofiltersFilterBackend
else:
    node_filter_backend = None
    node_filter_set = None