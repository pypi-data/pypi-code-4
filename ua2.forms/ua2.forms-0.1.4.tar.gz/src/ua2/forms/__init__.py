from django import forms
from ua2.forms.base import BaseForm
from django.db import models
from django.db.models.fields import FieldDoesNotExist

__all__ = ['RequestForm', 'RequestModelForm']


class RequestModelForm(BaseForm, forms.ModelForm):
    _ref_class = forms.ModelForm


class RequestForm(BaseForm, forms.Form):
    _ref_class = forms.Form

    def set_model_fields(self, instance, exclude_fields=None):
        '''Fills values from the form fields into instance fields'''
        exclude = exclude_fields or []
        data = self.cleaned_data
        for key in data:
            #print key, data[key], type(data[key])
            if key in instance._meta.get_all_field_names() and not key in exclude:
                field = instance._meta.get_field(key)
                if (type(field) in [models.ImageField, models.FileField]):
                    if data[key] != None:
                        if data[key] == False:
                            data[key] = None
                        setattr(instance, '%s' % key, data[key])
                elif (type(field)) in [models.ForeignKey,
                                       models.IPAddressField,
                                       models.GenericIPAddressField]:
                    if not data[key] == '':
                        setattr(instance, '%s' % key, data[key])
                else:
                    setattr(instance, '%s' % key, data[key])

    def set_initial(self, instance):
        for fieldname in self.fields.keys():
            field = self.fields[fieldname]
            try:
                field_type = type(instance._meta.get_field(fieldname))
            except FieldDoesNotExist:
                continue

            if fieldname in self.initial:
                continue
            if hasattr(instance, '%s' % fieldname):
                attr = getattr(instance, '%s' % fieldname)
                if callable(attr):
                    attr = attr()
                #print "%s %s %s=%s(%s)" % (field, field_type,
                #    fieldname, attr, type(attr))
                if not attr:
                    continue
                if type(field) == forms.ModelMultipleChoiceField:
                    self.initial[field] = attr.all()
                elif field_type == models.ManyToManyField:
                    self.initial[fieldname] = [t.pk for t in attr.all()]
                elif field_type == models.ForeignKey:
                    self.initial[fieldname] = attr.pk
                else:
                    self.initial[fieldname] = attr
