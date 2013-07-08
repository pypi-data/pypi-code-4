from django import forms
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.forms.base import BaseForm
from djinn_announcements.models.announcement import Announcement


class AnnouncementForm(BaseForm):

    text = forms.CharField(label=_("Announcement text"),
                           help_text=_("200 characters max"),
                           max_length=200,
                           widget=forms.Textarea(
            attrs={'rows': '5', 'class': 'count_characters', 
                   'data-maxchars': '200'}),
                           )

    @property
    def labels(self):

        return {'submit': _('Save announcement'),
                'cancel': _('Cancel'),
                'header': _('Add announcement')}

    class Meta(BaseForm.Meta):
        model = Announcement
        fields = ("title", "text")
