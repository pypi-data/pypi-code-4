from django import forms
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.forms.base import PartialUpdateMixin
from djinn_announcements.models.announcementupdate import AnnouncementUpdate
from django.template.defaultfilters import removetags


class AnnouncementUpdateForm(PartialUpdateMixin, forms.ModelForm):

    date = forms.DateTimeField(label=_("Date"),
                               widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
            )
                               )    
    text = forms.CharField(label=_("Description"),
                           max_length=150,
                           help_text="Maximaal 150 karakters",
                           widget=forms.Textarea(
            attrs={'class': 'full wysiwyg',
                   'data-maxchars': 150,
                   'rows': '5'})
                             )

    @property
    def labels(self):

        return {'submit': 'Opslaan', 'cancel': 'Annuleren'}

    def clean_text(self):

        value = self.cleaned_data['text'] or ""

        return removetags(value, 'script')

    class Meta:
        model = AnnouncementUpdate
        widgets = {'announcement': forms.HiddenInput()}
