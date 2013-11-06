#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from sqlalchemy.schema          import MetaData
#from sqlalchemy.exc             import IntegrityError
#from formalchemy                import FieldSet

from django                    import forms
from django.utils.translation  import ugettext as  _
from blogengine.contrib.api_v1 import CategoryManager
from widgets import *

__all__ = ['DynamicField', 'EntryForm', 'DeleteForm']

class DynamicField(forms.ChoiceField):
    '''ChoiceField subclass with builtin autocomplete widget functionality
    
    By default, use the ``choices`` argument as default iterable of values.
    '''

    def __init__(self, *args, **kwargs):
        # initialize autocomplete widget
        kwargs['widget'] = DynamicTextInput(kwargs['choices'])
        super(DynamicField, self).__init__(*args, **kwargs)

class SendToFriendForm(forms.Form):
    recipient1 = forms.EmailField(required=True)
    recipient2 = forms.EmailField(required=False, help_text='Optional field')
    recipient3 = forms.EmailField(required=False, help_text='Optional field')
    
    name = forms.CharField(required=True, label=_('Your name'))
    subject = forms.CharField(required=True, label=_('Subject'))
    message = forms.CharField(required=False, \
        label=_('Private message'), \
        widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))

#class ConfirmActionForm(forms.Form):
#    yesno_choice = forms.BooleanField(required=True)

class EntryForm(forms.Form):
    """Basic article entry form.""" 

    category_choices = [
        ("%s".lower()%item, str(item))for item in CategoryManager.objects.all()
        ]
    
    title = forms.CharField(required=True, label=_('Title'))
    
    # todo: add jquery autocomplete widget here from camelia 1.0
    category = DynamicField(choices=category_choices, \
        required=True, label=_('Category'))
    
    # source file (rst or markdown formats) to upload and convert
    # in sanitized markup
    #source = forms.CharField(
    #    #upload_to='uploads', \
    #    required=True, \
    #    label=_('File'), \
    #    widget=forms.FileInput(), \
    #    help_text=_('Valid file formats: rest, markdown, xhtml')
    #    )
            
    # think metadata like annotations
    short_description = forms.CharField(required=True, label=_('Summary'), \
        widget=forms.TextInput(),
        help_text=_('Summary of the article (140 characters or less!)')
        )
    # publish now?    
    reviewed = forms.BooleanField(required=False, initial=True)
    # this needs to be prepopulated..
    slug = forms.CharField(required=True)
    
    body = forms.CharField(_('Content'), \
        widget=forms.Textarea(attrs={'rows':10, 'cols':40}),
        required=True, help_text=_('You can use markdown syntax here'))

#AddEntryForm = EntryForm

class DeleteForm(forms.Form):
    confirm_unpublish = forms.BooleanField(label=_('Unpublish this entry?'), required=False, initial=True)
    confirm_delete = forms.BooleanField(label=_('Delete this entry permanently?'), required=True, initial=False)

