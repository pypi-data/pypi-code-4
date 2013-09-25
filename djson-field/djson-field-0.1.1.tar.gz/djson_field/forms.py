# -*- coding: utf-8 -*-
from django.forms import CharField
from djson_field.widgets import JSONWidget

import json


def mask(initial, value):
    if isinstance(initial, dict):
        if isinstance(value, dict):
            masked = {}
            for k, v in initial.iteritems():
                masked[k] = mask(v, value[k]) if k in value else v
            return masked
        else:
            return initial
    elif isinstance(initial, list):
        if isinstance(value, list):
            masked = []
            for i, v in enumerate(initial):
                masked.append(mask(v, value[i]) if len(value) > i else v)
            return masked
        else:
            return initial
    else:
        return value


class JsonField(CharField):

    def __init__(self, *args, **kwargs):
        self.is_masked = kwargs.pop("is_masked", False)
        kwargs['widget'] = JSONWidget(rules=kwargs.pop('rules', []))
        return super(JsonField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        value = value or ""
        if self.is_masked:
            value = json.dumps(mask(
                json.loads(self.initial), json.loads(value)
            ))
        return super(JsonField, self).prepare_value(value)
