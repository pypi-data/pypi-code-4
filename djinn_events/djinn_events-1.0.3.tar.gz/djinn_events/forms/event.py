from urllib import unquote_plus
from django import forms
from django.utils.translation import ugettext_lazy as _
from djinn_forms.widgets.link import LinkWidget
from djinn_events.models.event import Event
from djinn_contenttypes.forms.base import BaseForm


class EventForm(BaseForm):

    start_date = forms.DateField(label=_("Start date"),
                                 widget=forms.DateTimeInput(
            attrs={'class': 'date', "placeholder": _("Date")},
            format="%d-%m-%Y"
            )
                                 )
    
    start_time = forms.TimeField(label=_("Start time"),
                                 required=False,
                                 widget=forms.TextInput(
            attrs={'class': 'time', 'size': 5, "placeholder": _("Time")},
            )
                                     )

    end_date = forms.DateField(label=_("End date"),
                               required=False,
                               widget=forms.DateInput(
            attrs={'class': 'date', "placeholder": _("Date")},
            format="%d-%m-%Y"
            )
                               )
    
    end_time = forms.TimeField(label=_("End time"),
                               required=False,
                               widget=forms.TextInput(
            attrs={'class': 'time', 'size': 5, "placeholder": _("Time")},
            )
                                     )

    title = forms.CharField(label=_("Title"),
                            help_text=_("50 characters max"),
                            max_length=50,
                           widget=forms.TextInput(
                attrs={'data-maxchars': 50,
                       'class': "count_characters"})
                           )

    location = forms.CharField(label=_("Location"),
                               help_text=_("50 characters max"),
                               required=False,
                               max_length=50,
                           widget=forms.TextInput(
                attrs={'data-maxchars': 50,
                       'class': "count_characters"})
                           )

    text = forms.CharField(label=_("Description"),
                           help_text=_("500 characters max"),
                           max_length=500,
                           widget=forms.Textarea(
                attrs={'data-maxchars': 500, 
                       'class': "count_characters",
                       'rows': '3'})
                           )

    link = forms.CharField(label=_("Link"),
                           required=False,
                           max_length=200,
                           widget=LinkWidget())

    def clean_link(self):
        
        """ Always store the unquoted version """
        
        return unquote_plus(self.cleaned_data['link'])

    def labels(self):

        return {'submit': _("Save event"), 
                'cancel': _("Cancel"),
                'header': _("Add event")}

    class Meta(BaseForm.Meta):
        model = Event
