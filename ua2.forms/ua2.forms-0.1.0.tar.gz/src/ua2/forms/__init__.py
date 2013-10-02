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
                if (type(instance._meta.get_field(key)) in
                    [models.ImageField, models.FileField]):
                    if data[key] != None:
                        if data[key] == False:
                            data[key] = None
                        setattr(instance, '%s' % key, data[key])
                else:
                    setattr(instance, '%s' % key, data[key])

    def set_initial(self, instance):
        for field in self.fields.keys():
            try:
                field_type = type(instance._meta.get_field(field))
            except FieldDoesNotExist:
                continue
            
            if field in self.initial:
                continue
            if hasattr(instance, '%s' % field):
                attr = getattr(instance, '%s' % field)
                if callable(attr):
                    attr = attr()
                #print "%s %s=%s(%s)" % (field_type, field, attr, type(attr))
                if field_type == models.ManyToManyField:
                    self.initial[field] = attr.all()
                elif field_type == models.ForeignKey:
                    self.initial[field] = attr.pk
                else:
                    self.initial[field] = attr


    def populate(self, field_name, queryset, add_empty=False, label_name=None,
                 value_name=None, empty_label=None, empty_value=None):
        """ Pupulate chouice field by given QuerySet
        Args:
            field_name: field name in form (as string)
            queryset: QierySet object
            add_empty: if set to True function prepend list of
                choices by empty line
            label_name: name of field, propery or method in queryset
                instance model, that will be set as label in dropdown
            value_name: name of field, propery or method in queryset
                instance model, that will be set as value in dropdown
            empty_label: value, that will be set for empty line,
                by defaylt it set to '-------'
            empty_value: value, that will be set for empty line,
                by default it set to ''

        """
        field = self.fields[field_name]

        field.choices = []
        if add_empty:
            field.choices.append((empty_label or '',
                                  empty_value or '-------'))



        def _get_field(obj, fieldname=None):
            if fieldname:
                value = getattr(obj, fieldname)
                if callable(value):
                    value = value()
            else:
                value = unicode(obj)
            return value

        for item in queryset:
            label = _get_field(item, label_name)
            value = _get_field(item, value_name or 'pk')
            field.choices.append((unicode(value),
                                  label))
