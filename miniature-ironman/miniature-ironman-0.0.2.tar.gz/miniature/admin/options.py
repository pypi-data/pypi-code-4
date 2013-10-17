# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

__author__ = 'ir4y'


def make_active(modeladmin, request, queryset):
    queryset.update(is_active=False)

make_active.short_description = _(u"Активировать")


def SlugAdminTraits(field_name='name'):
    slug_field_name = field_name + "_slug"

    class _SlugAdminMixin(object):
        def __init__(self, *args, **kwargs):
            if not self.readonly_fields:
                self.readonly_fields = []
            self.readonly_fields.extend([slug_field_name])
            super(_SlugAdminMixin, self).__init__(*args, **kwargs)
    return _SlugAdminMixin
