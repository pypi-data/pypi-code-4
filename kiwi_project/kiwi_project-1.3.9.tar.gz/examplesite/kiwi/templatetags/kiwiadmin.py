# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django import template
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe

from Sveetchies.django.utils import get_string_or_variable
from Sveetchies.django.TreeMaker import TemplatedTree

from kiwi.models import Wikipage

register = template.Library()

@register.filter(name='indenter')
def indenter(value, coef=20):
    #return mark_safe(indent_string*value)
    return (value+1)*coef
