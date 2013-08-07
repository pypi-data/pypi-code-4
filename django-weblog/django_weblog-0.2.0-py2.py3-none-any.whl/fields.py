# encoding: utf-8
"""
Extra form fields for the weblog app.

"""
from django import forms
from django.utils.encoding import smart_unicode


class CategoryModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        """This method generates the labes for the choices presented by this
        object."""
        return smart_unicode(obj.form_display_name)


class CategoryModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        """This method generates the labels for the choices presented by this
        object."""
        return smart_unicode(obj.form_display_name)
