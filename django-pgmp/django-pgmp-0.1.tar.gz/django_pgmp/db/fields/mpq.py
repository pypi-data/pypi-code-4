#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === django_pgmp.db.fields.mpq -------------------------------------------===
# This file is part of django-pgpm. django-pgpm is copyright © 2012, RokuSigma
# Inc. and contributors. See AUTHORS and LICENSE for more details.
#
# django-pgpm is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# django-pgpm is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-pgpm. If not, see <http://www.gnu.org/licenses/>.
# ===----------------------------------------------------------------------===

import six

try:
    from gmpy2 import mpq
except ImportError:
    from gmpy import mpq

from django.utils.translation import ugettext_lazy as _

from django import forms
class MultiPrecisionFractionFormField(forms.FloatField):
    def clean(self, value):
        try:
            return unicode(mpq(value))
        except Exception, e:
            six.reraise(forms.ValidationError, _(u"unable to convert "
                u"string to GNU MP mpq_t value: %s" % unicode(e)))

from django.db import models
class MultiPrecisionFractionField(models.FloatField):
    description = "An arbitrary precision fraction type."
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'mpq'

    def get_internal_type(self):
        return "MultiPrecisionFractionField"

    def get_prep_value(self, value):
        if value is None:
            return None
        return '/'.join(map(str, (value.numerator, value.denominator)))

    def to_python(self, value):
        if value is None:
            return value
        try:
            return mpq(value)
        except (TypeError, ValueError):
            msg = self.error_messages['invalid'] % str(value)
            raise exceptions.ValidationError(msg)

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', MultiPrecisionFractionFormField)
        return super(MultiPrecisionFractionField, self).formfield(**kwargs)

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = '.'.join([
            self.__class__.__module__,
            self.__class__.__name__])
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
