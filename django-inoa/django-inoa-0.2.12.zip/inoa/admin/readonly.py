# -*- coding: utf-8 -*-
from django.contrib.admin.util import flatten_fieldsets


class ReadonlyFieldsOnUpdateMixin(object):
    """
    Use this mixin in your ModelAdmin class to make some fields read-only when
    updating an existing item (but leaving them editable for new items).
    Such fields should be defined in a 'readonly_fields_on_update' attribute in your class.
    If not explicitly defined, all fields will be made readonly when changing an existing object.
    Overrides can be given through an optional 'editable_fields_on_update' attribute in your class;
    these will be kept editable even if they are matched in 'readonly_fields_on_update'.
    """
    def get_readonly_fields(self, request, obj=None):
        fields = super(ReadonlyFieldsOnUpdateMixin, self).get_readonly_fields(request, obj)
        if hasattr(self, 'avoid_readonly_recursion'):
            return fields

        readonly = []
        extra_fields = getattr(self, 'readonly_fields_on_update', None)
        if obj is None:
            readonly = fields
        elif extra_fields is None:
            if self.declared_fieldsets:
                fields = flatten_fieldsets(self.declared_fieldsets)
            else:
                self.avoid_readonly_recursion = True
                if hasattr(self, 'get_form'):
                    form = self.get_form(request, obj)
                else:
                    form = self.get_formset(request, obj).form
                del self.avoid_readonly_recursion
                fields = fields + fields.__class__(form.base_fields.keys())
            readonly = fields
        else:
            readonly = fields + fields.__class__(extra_fields)

        editable_fields = getattr(self, 'editable_fields_on_update', None)
        if editable_fields:
            readonly = [field for field in readonly if field not in editable_fields]

        return readonly
