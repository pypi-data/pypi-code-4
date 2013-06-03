from __future__ import unicode_literals

from django.template import Library
from django.utils.translation import get_language

register = Library()


@register.assignment_tag
def translate(obj, language=None):
    language = language or get_language()
    try:
        return obj.translations.lang(language).get()
    except:
        return obj