# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter(name='calcul_indent')
def calcul_indent(value, coef=20):
    return (value+1)*coef
    #return value*coef
