### -*- coding: utf-8 -*- ####################################################

from django import template
from django.conf import settings

from ..models import Provider

register = template.Library()

@register.inclusion_tag('smscoin_help.html', takes_context=True)
def smscoin_help(context):
    """Helper for user to choose provider in his country."""
    return {
        'providers': [(n, Provider.objects.filter(country=c).order_by('name')) for c,n in Provider.get_sorted_countries()], 
        'selected_provider': int(context['request'].REQUEST.get('provider', 0) or 0), 
        'key': settings.SMSCOIN_KEY
    }
