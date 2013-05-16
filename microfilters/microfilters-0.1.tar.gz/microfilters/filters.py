# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
import six


class Filter(object):

    def sanitize(self, value):
        return value

    def filter(self, item_list, value):
        return item_list


class FilterSet(Filter):

    def __init__(self, filters):
        assert isinstance(filters, dict), 'The "filters" argument has do be of type "dict"'
        self._filters = filters

    def filter(self, item_list, value_dict):
        for key in six.iterkeys(value_dict):
            if key in six.iterkeys(self._filters):
                value = self._filters[key].sanitize(value_dict[key])
                item_list = self._filters[key].filter(item_list, value)
        return item_list