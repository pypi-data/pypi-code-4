from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _
from modelfeedback.models import Feedback


class FeedbackForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_user(self):
        data = self.cleaned_data['user']

        if self.user != data:
            raise ValidationError(
                _('Sorry, but we cannot understand your request.'))

        return data

    class Meta:
        model = Feedback
