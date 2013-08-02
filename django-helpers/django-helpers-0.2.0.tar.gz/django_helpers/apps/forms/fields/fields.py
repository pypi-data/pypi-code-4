# coding=utf-8
__author__ = 'ajumell'
from django import forms
from ..widgets import bootstrap

GenericIPAddressField = forms.GenericIPAddressField
FilePathField = forms.FilePathField
SlugField = forms.SlugField
TypedChoiceField = forms.TypedChoiceField
TypedMultipleChoiceField = forms.TypedMultipleChoiceField
SplitDateTimeField = forms.SplitDateTimeField
ComboField = forms.ComboField
MultiValueField = forms.MultiValueField
NullBooleanField = forms.NullBooleanField
RegexField = forms.RegexField


class CharField(forms.CharField):
    pass


class PasswordField(forms.CharField):
    widget = forms.PasswordInput


class DateField(forms.DateField):
    widget = bootstrap.DatePickerWidget


class DateTimeField(forms.DateTimeField):
    widget = bootstrap.DateTimePickerWidget


class TimeField(forms.TimeField):
    widget = bootstrap.TimePickerWidget


class MultipleChoiceField(forms.MultipleChoiceField):
    widget = bootstrap.MultiSelectWidget


class ChoiceField(forms.ChoiceField):
    widget = bootstrap.SelectWidget


class BooleanField(forms.BooleanField):
    widget = bootstrap.SwitchWidget


class DecimalField(forms.DecimalField):
    pass


class URLField(forms.URLField):
    pass


class IPAddressField(forms.IPAddressField):
    pass


class ModelChoiceField(forms.ModelChoiceField):
    pass


class EmailField(forms.EmailField):
    pass


class FileField(forms.FileField):
    pass


class IntegerField(forms.IntegerField):
    pass


class FloatField(forms.FloatField):
    pass


class FileField(forms.FileField):
    pass


class ImageField(forms.ImageField):
    pass

