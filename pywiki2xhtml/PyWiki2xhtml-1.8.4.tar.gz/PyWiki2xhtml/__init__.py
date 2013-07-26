# -*- coding: utf-8 -*-
__all__ = ["parser", "helper", "flat2tree"]
__title__ = "PyWiki2Xhtml, a python transformer from Wiki syntax to XHTML"
__version__ = "1.8.4"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2007-2011 Sveetch.biz"
__license__ = "GPL"

DEFAULT_CONFIGSET = {
    # Toute les options sauf le menu de titre
    'standard': {
        'active_menu_title': False,
        'active_wikiwords': True,
        'active_footnotes': True,
        'absolute_path_wikiroot': '/%s/',
        'absolute_path_createpage': None,
    },
    # Toute les options avec le menu de titre
    'standard_with_summary': {
        'active_menu_title': True,
        'active_wikiwords': True,
        'active_footnotes': True,
        'absolute_path_wikiroot': '/%s/',
        'absolute_path_createpage': None,
    },
    # Options limités pour les textes "courts" (résumés, introductions, etc.. en dehors 
    # du context d'un wiki)
    'short': {
        'active_hr': False,
        'active_menu_title': False,
        'active_wikiwords': False,
        'active_footnotes': False,
        'active_embeds': False,
        'active_title': False,
        'absolute_path_createpage': None,
    },
}
