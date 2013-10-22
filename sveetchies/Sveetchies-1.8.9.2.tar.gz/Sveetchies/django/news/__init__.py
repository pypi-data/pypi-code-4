# -*- coding: utf-8 -*-
"""
Brique de simples billets d'actualités

============
Installation
============

Requis :

* Django >= 1.3.x;
* PyWiki2Xhtml;
* Sveetchies;

Ce module est à déclarer comme application d'un projet Django dans 
``settings.INSTALLED_APPS`` tel que : ::

    INSTALLED_APPS = (
        'Sveetchies.django.pywiki2xhtml',
        'Sveetchies.django.attachments',
        'Sveetchies.django.news',
        ...
        'yourapps'
    )

TODO: Pour les preview, ce serait plusse mieux bien de spécifier les médias dans les 
      métas du modèle admin, mais le concept de Grapelli qui importe ses CSS avec @ 
      casserait tout, vu que Django importe les médias déclarés directement sans 
      utiliser un @import, du coup ils ne seraient pas pris en compte. Tester si on 
      peut pas tricher en spécifiant qu'une feuille unique contenant des @import sur 
      les css nécessaires au BOF editor;
"""
from django.conf import settings
from django import template

__version__ = '0.1.2'

NEWS_ENTRIES_PAGINATION = getattr(settings, 'NEWS_ENTRIES_PAGINATION', 15)
NEWS_LASTNEWS_TAGS_TEMPLATE = getattr(settings, 'NEWS_LASTNEWS_TAGS_TEMPLATE', 'news/last_news_entry.html')

template.add_to_builtins("Sveetchies.django.tags.common_filters")
template.add_to_builtins("Sveetchies.django.tags.pagination")
template.add_to_builtins("Sveetchies.django.attachments.templatetags.attachments_tags")
