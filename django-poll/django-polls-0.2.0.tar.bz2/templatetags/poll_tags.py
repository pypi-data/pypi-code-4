import math

from django.template.loader import get_template
from django import template

from polls.forms import PollVoteForm
from polls.methods import get_poll_form, get_poll_vote_form

from coffee.mixins import FormMixin

register = template.Library()

COLORS = [
    'aqua',
    'black',
    'blue',
    'fuchsia',
    'gray',
    'green',
    'lime',
    'maroon',
    'navy',
    'olive',
    'orange',
    'purple',
    'red',
    'silver',
    'teal',
    'white',
    'yellow'
]


@register.inclusion_tag('polls/poll/partial/poll.html')
def poll_form(instance, request):
    form, formset = get_poll_form(instance, request)
    
    coffee = FormMixin()
    
    placeholders = {
        'question': 'Question'
    }
    
    coffee.construct_widgets(form.fields, placeholders, must_delete=False)
    
    return {'form': form, 'formset': formset}


@register.inclusion_tag('polls/partial/vote.html')
def poll_vote(instance):
    form = get_poll_vote_form(instance)

    return {'form': form, 'instance': instance}


@register.simple_tag
def get_colors():
    return COLORS


@register.simple_tag
def get_color(index):
    return COLORS[index]


@register.simple_tag(takes_context=True)
def get_data(context):
    poll = context['poll']

    data = []

    for choice in poll.choice_set.all():
        data.append([str(choice.choice_text), float(choice.percentage)])

    return data
