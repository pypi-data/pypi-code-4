# coding=utf-8
from django import template
from django_helpers.utils import models

register = template.Library()


@register.simple_tag(takes_context=False)
def last_query():
    return models.last_query()


