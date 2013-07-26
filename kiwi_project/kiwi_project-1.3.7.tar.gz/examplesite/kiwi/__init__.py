# -*- coding: utf-8 -*-
"""
Kiwi est un module Django dont le but est de gérer des pages Wiki
"""
from django.conf import settings
from django import template

__version__ = '1.3.7'

WIKIPAGE_ENABLE_ARCHIVE = getattr(settings, 'WIKIPAGE_ENABLE_ARCHIVE', True)
WIKIPAGE_ARCHIVED_DEFAULT = getattr(settings, 'WIKIPAGE_ARCHIVED_DEFAULT', WIKIPAGE_ENABLE_ARCHIVE)
KIWI_MEDIA_PREFIX = getattr(settings, 'KIWI_MEDIA_PREFIX', 'kiwi/')
PyWiki2Xhtml_ConfigSet = getattr(settings, 'PYWIKI2XHTML_CONFIGSET', {
        'standard': {
            'active_menu_title': False,
            'active_wikiwords': True,
            'active_footnotes': True,
            'absolute_path_wikiroot': '/%s/',
            'absolute_path_createpage': None,
            'macro_mediaplayer_url': '%sflash/mediaplayer/player.swf'%settings.MEDIA_URL,
        },
        'standard_with_summary': {
            'active_menu_title': True,
            'active_wikiwords': True,
            'active_footnotes': True,
            'absolute_path_wikiroot': '/%s/',
            'absolute_path_createpage': None,
            'macro_mediaplayer_url': '%sflash/mediaplayer/player.swf'%settings.MEDIA_URL,
        }
    }
)

template.add_to_builtins("Sveetchies.django.tags.pagination")