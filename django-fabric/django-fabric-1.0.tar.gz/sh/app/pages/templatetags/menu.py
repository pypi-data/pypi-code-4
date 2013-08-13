# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template.base import Library
from sh.app.pages.models import Page

register = Library()

@register.inclusion_tag('pages/templatetags/menu.html')
def main_menu():

    pages = cache.get('mainnav')
    if pages is None:
        pages = Page.objects.all().order_by('weight')
        cache.set('mainnav', pages)

    return {'pages': pages}

