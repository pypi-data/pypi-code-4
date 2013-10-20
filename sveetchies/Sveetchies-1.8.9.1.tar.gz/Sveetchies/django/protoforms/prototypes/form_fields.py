# -*- coding: utf-8 -*-
import datetime

from django import forms
from django.contrib.localflavor.fr.forms import FRZipCodeField

from Sveetchies.django.protoforms.models import SelectionValueExtension, SelectionItem

from Sveetchies.django.protoforms.prototypes.model_fields import ForeignKeySelectionModelField, ManyToManySelectionModelField

class ExtendedSelectionItemFormField(forms.CharField):
    """
    Simple héritage sans modification juste pour avoir une signature explicite
    """
    pass

class ForeignKeySelectionFormField(forms.ModelChoiceField):
    """
    Champs de séléction d'après SelectionItem
    """
    def __init__(self, empty_label=u"---------", cache_choices=False,
                 required=True, widget=None, label=None, initial=None,
                 help_text=None, to_field_name=None, *args, **kwargs):
        
        self.collectorform_selectionitem_choices = kwargs['selectionitem_choices']
        del kwargs['selectionitem_choices']
        queryset = SelectionItem.objects.filter(kind=self.collectorform_selectionitem_choices).order_by('order', 'label')
        
        super(ForeignKeySelectionFormField, self).__init__(queryset, empty_label=empty_label, cache_choices=cache_choices,
                 required=required, widget=widget, label=label, initial=initial,
                 help_text=help_text, to_field_name=to_field_name, *args, **kwargs)

class ManyToManySelectionFormField(forms.ModelMultipleChoiceField):
    """
    Champs de séléction multiple d'après SelectionItem
    """
    def __init__(self, selectionitem_choices=None, *args, **kwargs):
        
        self.collectorform_selectionitem_choices = selectionitem_choices
        queryset = SelectionItem.objects.filter(kind=self.collectorform_selectionitem_choices).order_by('order', 'label')
        
        super(ManyToManySelectionFormField, self).__init__(queryset, *args, **kwargs)

class ProtoFRZipCodeField(FRZipCodeField):
    """
    Amélioration de `django.contrib.localflavor.fr.form.FRZipCodeField` pour pallier à 
    son défaut de non validation réelle des départements (genre pour 00000 ou 99000)
    """
    def clean(self, value):
        cleaned = super(ProtoFRZipCodeField, self).clean(value)
        # Vérifie que les deux premiers digits du code postal est compris entre 1 et 98 
        # compris (pas de département commencant par 00 ou 99)
        if int(cleaned[:2]) > 0 and int(cleaned[:2]) < 99:
            return cleaned
        raise forms.ValidationError(self.error_messages['invalid'])

class ProtoDateField(forms.DateField):
    """
    Amélioration de `forms.DateField` pour empêcher de soumettre une date qui est 
    supérieure à la date en cours
    """
    def clean(self, value):
        cleaned = super(ProtoDateField, self).clean(value)
        if cleaned and cleaned>datetime.date.today():
            raise forms.ValidationError(self.error_messages['invalid'])
        return cleaned
