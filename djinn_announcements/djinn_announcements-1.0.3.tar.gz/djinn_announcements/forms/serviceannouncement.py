from django import forms
from django.utils.translation import ugettext_lazy as _
from lxml.html.soupparser import fromstring
from djinn_contenttypes.forms.base import BaseForm
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from djinn_announcements.settings import SERVICEANNOUNCEMENT_STATUS_VOCAB, \
    ANNOUNCEMENT_PRIORITY_VOCAB


class ServiceAnnouncementForm(BaseForm):
    
    start_date = forms.DateTimeField(label=_("Start date"),
                                     widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
            )
                                     )

    end_date = forms.DateTimeField(label=_("(Expected) end date"),
                                     required=False,
                                     widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
            )
                                     )
    
    status = forms.IntegerField(label=_("Status"),
                                required=False,
                                initial=-1,
                                widget=forms.Select(
            choices=SERVICEANNOUNCEMENT_STATUS_VOCAB)
                                )

    priority = forms.IntegerField(label=_("Priority"),
                                  initial=0,
                                  widget=forms.Select(
            choices=ANNOUNCEMENT_PRIORITY_VOCAB)
                                  )

    text = forms.CharField(label=_("Description"),
                           help_text="Maximaal 300 karakters",
                           max_length=300,
                           widget=forms.Textarea(
            attrs={'class': 'full wysiwyg',
                   'data-maxchars': 300,
                   'rows': '5'})
    )

    def clean_text(self):

        data = self.cleaned_data['text'] or ""

        html = fromstring(data)

        chars = len(html.text_content())

        if chars > 150:
            raise forms.ValidationError(
                _(u'Ensure this value has at most 150 characters '
                  '(it has %d).' % chars))

        return data

    class Meta(BaseForm.Meta):
        model = ServiceAnnouncement
