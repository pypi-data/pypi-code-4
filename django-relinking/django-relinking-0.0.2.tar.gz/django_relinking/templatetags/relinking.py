# coding: utf-8
from django import template
from django.utils.safestring import mark_safe
from django_relinking import relink_text


register = template.Library()


@register.filter
def relink(origin):
    """
    Relink origin text
    """
    return mark_safe(relink_text(origin))
