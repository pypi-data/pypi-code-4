from django.template.loader import get_template
from django import template

from polls.forms import PollVoteForm
from polls.methods import get_poll_form, get_poll_vote_form

register = template.Library()

@register.inclusion_tag('polls/poll/partial/poll.html')
def poll_form(instance, request):
    form, formset = get_poll_form(instance, request)
    
    return {'form': form, 'formset': formset}
    
@register.inclusion_tag('polls/partial/vote.html')
def poll_vote(instance):
    form = get_poll_vote_form(instance)
    
    return {'form': form, 'instance': instance}