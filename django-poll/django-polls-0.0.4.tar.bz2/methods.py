from django.forms.models import inlineformset_factory

from polls.models import Choice, Poll
from polls.forms import PollForm, PollVoteForm

def get_poll_form(instance, request):
    data = request.POST
    if not data:
        form = PollForm(instance=instance)
        ChoiceFormSet = inlineformset_factory(Poll, Choice)
        formset = ChoiceFormSet(instance=instance)
    else:
        ChoiceFormSet = inlineformset_factory(Poll, Choice)
            
        form = PollForm(data, instance=instance) if instance else PollForm(data)
        form.instance.user = request.user
        formset = ChoiceFormSet(data, instance=form.instance)
    
    return (form, formset)
    
def get_poll_vote_form(instance):
    form = PollVoteForm()
    form.construct(instance)
    
    return form