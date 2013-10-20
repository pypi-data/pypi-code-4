# -*- coding: utf-8 -*-
"""
Map des modèles de données dans l'administration de Django
"""
from django.contrib.admin import ModelAdmin

from Sveetchies.django.protoforms.models import SelectionItem, SelectionValueExtension

class BaseContainerAdmin(ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form_object = super(BaseContainerAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            extensions = {}
            # Retrouve tout les champs de séléctions qui ont une valeur étendue et 
            # inscrit leur valeur dans un registre rangé par le nom clé de champs de 
            # séléction
            for field_name in form_object.Meta.fields:
                model_field = getattr(obj, field_name)
                if isinstance(model_field, SelectionItem):
                    if model_field.value_extended:
                        try:
                            extension_value = obj.extensions.get(extended_field=field_name).value
                        except SelectionValueExtension.DoesNotExist:
                            pass
                        else:
                            extensions[field_name] = extension_value
            form_object.cf_extension_fields_values = extensions
        return form_object
