# -*- coding: utf-8 -*-
"""
Brique pour gérer des fichiers à joindre à des objets

Système ultra-simple tiré de Kiwi, reporté dans Sveetchies pour pouvoir l'utiliser 
ailleurs sans dépendre de Kiwi.
"""
from django.conf import settings
from django import template

__version__ = '0.1.0'

ATTACHMENTS_WIDGET_TEMPLATEPATH = getattr(settings, 'ATTACHMENTS_WIDGET_TEMPLATEPATH', 'attachments/attachments_widget.html')
ATTACHMENTS_FILE_UPLOADPATH = getattr(settings, 'ATTACHMENTS_FILE_UPLOADPATH', 'attachments/%Y/%m/%d')
