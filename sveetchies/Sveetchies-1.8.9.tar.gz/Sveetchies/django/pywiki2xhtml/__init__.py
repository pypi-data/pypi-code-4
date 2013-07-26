# -*- coding: utf-8 -*-
"""
Surcouche Django pour utiliser PyWiki2Xhtml

============
Installation
============

Requis :

* PyWiki2Xhtml
* Django >= 1.3.x
* Sveetchies

Ce module est à déclarer comme application d'un projet Django dans 
``settings.INSTALLED_APPS`` tel que : ::

    INSTALLED_APPS = (
        'Sveetchies.django.pywiki2xhtml',
        ...
        'yourapps'
    )
"""
from django.conf import settings
from django import template
from PyWiki2xhtml import DEFAULT_CONFIGSET

__version__ = '0.1.0'

PYWIKI2XHTML_CONFIGSET = getattr(settings, 'PYWIKI2XHTML_CONFIGSET', DEFAULT_CONFIGSET)
PYWIKI2XHTML_CONTAINER = getattr(settings, 'PYWIKI2XHTML_CONTAINER', u'<div class="wiki2xhtml">{content}</div>')
PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS = getattr(settings, 'PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS', ('attach', 'mediaplayer', 'pygments', 'googlemap'))

template.add_to_builtins("Sveetchies.django.pywiki2xhtml.templatetags.pywiki2xhtml_markup")
