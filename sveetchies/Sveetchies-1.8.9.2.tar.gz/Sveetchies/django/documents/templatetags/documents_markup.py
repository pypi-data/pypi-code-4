# -*- coding: utf-8 -*-
"""
Tags du parser
"""
from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from Sveetchies.django.documents.parser import SourceParser
from Sveetchies.django.documents.templatetags import get_render_with_cache, get_toc_with_cache

register = template.Library()

def source_render(source, setting_key="default"):
    """
    Rendu d'un texte fournit le parser
    """
    return mark_safe( SourceParser(source, setting_key=setting_key) )
source_render.is_safe = True
register.filter(source_render)

def document_render(document_instance, setting_key="default"):
    """
    Rendu du contenu d'une instance (Page ou Insert)
    """
    return mark_safe( get_render_with_cache(document_instance, setting_key=setting_key) )
document_render.is_safe = True
register.filter(document_render)

def document_toc(document_instance, setting_key="default"):
    """
    TOC(sommaire des titres) du contenu d'une instance (Page ou Insert)
    """
    return mark_safe( get_toc_with_cache(document_instance, setting_key=setting_key) )
document_toc.is_safe = True
register.filter(document_toc)
