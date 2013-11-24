# -*- coding: utf-8 -*-

"""Module containing forms mixins."""

from ui_permissions.descriptor.resource import Resource


class UiPermFormMixin(object):

    """Mixin that allows passing extra keyword argument into form class constructor."""

    def __init__(self, **kwargs):
        self.resource_desc = kwargs.pop('resource_desc', Resource())
        super(UiPermFormMixin, self).__init__(**kwargs)


class UiPermModelFormMixin(UiPermFormMixin):

    """Mixin used with model form classes."""

    def _clean_form(self):
        for field_name in self.resource_desc.get_excluded_fields(self.fields.keys()):
            if hasattr(self.instance, field_name):
                self.cleaned_data[field_name] = getattr(self.instance, field_name)
        super(UiPermModelFormMixin, self)._clean_form()

    def _get_validation_exclusions(self):
        exclude = super(UiPermModelFormMixin, self)._get_validation_exclusions()
        exclude.extend(self.resource_desc.get_excluded_fields(self.fields.keys()))
        return list(set(exclude))
