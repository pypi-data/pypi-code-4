from django import forms

from polls.models import Poll, Choice

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        exclude = ('user',)
        
class PollVoteForm(forms.Form):
    choice = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)