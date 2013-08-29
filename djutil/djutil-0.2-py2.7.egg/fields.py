#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import CharField
from django.utils.crypto import get_random_string, random
from django.utils import six

ALLOWED_CHARS = "0123456789"


class CodeField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = kwargs.get("max_length", 5)
        kwargs["unique"] = kwargs.get("unique", True)

        if "db_index" not in kwargs:
            kwargs["db_index"] = True

        self.allowed_range = kwargs.pop("allowed_range", None)
        self.allowed_chars = kwargs.pop("allowed_chars", ALLOWED_CHARS)

        # When using model inheritance, set manager to search for matching
        # code values
        self.manager = kwargs.pop("manager", None)

        super(CodeField, self).__init__(*args, **kwargs)

    def pre_save(self, instance, add):
        value = self.value_from_object(instance)
        manager = self.manager
        if not value:
            value = generate_unique_code(
                self, instance, manager,
                length=self.max_length,
                allowed_range=self.allowed_range,
                allowed_chars=self.allowed_chars,
            )
            # Make the updated value available as instance attribute
            setattr(instance, self.name, value)
        return value

    def south_field_triple(self):
        """Returns a suitable description of this field for South."""
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return "djutil.fields.CodeField", args, kwargs


def generate_unique_code(field, instance, manager, length,
                         allowed_range, allowed_chars):
    if not manager:
        manager = type(instance).objects

    # Keep changing the code until it is unique
    for i in six.moves.xrange(1000):
        code = generate_code(length, allowed_range, allowed_chars)

        # Find instances with same code
        lookups = {"{}__iexact".format(field.name): code}
        rivals = manager.filter(**lookups).exclude(pk=instance.pk)

        if not rivals:
            # The code is unique, no model uses it
            return code

    raise ValueError("Could not generate unique code for "
                     "model: {}".format(instance))


def generate_code(length=5, allowed_range=None, allowed_chars=ALLOWED_CHARS):
    """
    If allowed range is specified, select number from range [a, b] inclusively.
    Otherwise pick from allowed chars.
    """
    if allowed_range:
        return str(random.randint(*allowed_range))
    else:
        return get_random_string(length, allowed_chars)
