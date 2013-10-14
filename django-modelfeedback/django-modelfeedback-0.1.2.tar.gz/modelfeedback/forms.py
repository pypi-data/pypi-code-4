from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from modelfeedback.models import Feedback


class FeedbackForm(forms.ModelForm):
    rating = forms.ChoiceField(widget=forms.RadioSelect,
                               choices=Feedback.RATING_CHOICES)
    message = forms.CharField(
        required=False,
        label="", widget=forms.Textarea(
            attrs={'placeholder': _('You can leave a message here.'),
                   'rows': 4,
                   'col': 10}))

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            self._update_errors(e.message_dict)

    class Meta:
        model = Feedback
        fields = ['rating', 'message']
