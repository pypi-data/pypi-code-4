# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.db import models
from djson_field.forms import JsonField

import json
import re
import string
_ = re.compile


class JSONField(models.TextField):
    """ Stores and loads valid JSON objects. """

    description = 'JSON object'
    BASE_RULES = [
        ([], {
            'type': models.CharField(max_length=""),
            'type_key': None,
            'actions': ['add_plain', 'add_list', 'add_dict'],
            'allow_removing': False,
            'allow_item_removing': False,
            'verbose_name': None,
            'help_text': None,
            'hidden': False,
        }),
        ([_(".*")], {
            'allow_removing': True,
        }),
    ]

    def __init__(self, *args, **kwargs):
        self.additional_rules = kwargs.pop('rules', [])
        self.initial = kwargs.pop('initial', {})
        self.additional_validators = kwargs.pop('additional_validators', [])
        self.is_masked = kwargs.pop('is_masked', False)
        super(JSONField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': JsonField}
        add_rules = self.additional_rules
        if hasattr(add_rules, '__call__'):
            add_rules = add_rules()
        defaults['rules'] = self.BASE_RULES + add_rules
        initial = self.initial
        if hasattr(initial, '__call__'):
            initial = initial()
        defaults['initial'] = json.dumps(initial)
        defaults['is_masked'] = self.is_masked
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)

    def validate_item(self, item, model_instance, path=[]):
        errors = []
        if isinstance(item, dict):
            for key, subitem in item.iteritems():
                errors += self.validate_item(
                    subitem, model_instance, path + [key]
                )
        elif isinstance(item, list):
            for i, subitem in enumerate(item):
                errors += self.validate_item(
                    subitem, model_instance, path + [i]
                )
        else:
            field = self.formfield()
            rules = field.widget.get_rules(path)
            field_type = rules['type']
            try:
                if isinstance(field_type, models.Field):
                    field_type.formfield().clean(item)
            except ValidationError as e:
                for msg in e.messages:
                    path = [unicode(ob) for ob in path]
                    errors.append(string.join(path, u" -> ") + u": " + unicode(msg))
        return errors

    def clean(self, value, model_instance):
        cleaned_data = super(JSONField, self).clean(value, model_instance)
        item = json.loads(value) if value else None
        errors = self.validate_item(item, model_instance)
        for validator in self.additional_validators:
            errors += validator(value)
        if len(errors) > 0:
            raise ValidationError(errors)
        return cleaned_data
