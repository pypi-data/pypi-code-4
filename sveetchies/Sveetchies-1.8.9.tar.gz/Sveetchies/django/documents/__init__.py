# -*- coding: utf-8 -*-
"""
Sveetchies-documents
"""
from django.conf import settings

__version__ = '0.8.0'

# Mots interdits/réservés pour les slugs des documents, sert à empêcher la création de 
# page avec un slug qui pourrait être déjà utilisé dans les urls et provoquer un conflit 
# avec une autre vue
DOCUMENTS_PAGE_RESERVED_SLUGS = getattr(settings, 'DOCUMENTS_PAGE_MENU', ('board','add','preview','documents-help','inserts'))

# Chemin du template par défaut pour la génération de menu d'arborescence dans les pages
DOCUMENTS_PAGE_TREEMENU = getattr(settings, 'DOCUMENTS_PAGE_TREEMENU', "documents/page_treemenu.html")
# Chemin du template par défaut pour la génération de menu "plat" dans les pages
DOCUMENTS_PAGE_FLATMENU = getattr(settings, 'DOCUMENTS_PAGE_FLATMENU', "documents/page_flatmenu.html")

# Choix du type d'éditeur à utiliser pour les textarea de textes ReST des formulaires, 
# peut être "supercodemirror", "markitup" ou ``None`` (qui désactive l'éditeur)
DOCUMENTS_EDITOR = getattr(settings, 'DOCUMENTS_EDITOR', "supercodemirror")

# Liste des templates disponibles pour les pages, attention à ne pas supprimer des 
# templates encore utilisés.
DOCUMENTS_PAGE_TEMPLATES = {
    'default': ('documents/page_details/default.html', u'Gabarit par défaut sans colonnes'),
    'column_by_2': ('documents/page_details/columned_bytwo.html', u'Gabarit colonné avec sommaire et navigation'),
}
DOCUMENTS_PAGE_TEMPLATES.update(getattr(settings, 'DOCUMENTS_PAGE_TEMPLATES', {}))

# Pour rendre silencieux les avertissements de lien wiki (via le role ``:page:xxx``) 
# vers une page qui n'existe pas (ou n'est pas visible). Désactivé par défaut, un 
# avertissement est affiché à l'édition et le ``:role:xxx`` est laissé en place.
# Si activé, en cas d'erreur le role est quand même transformé en lien et aucun 
# avertissement n'est affiché à l'édition.
DOCUMENTS_PARSER_WIKIROLE_SILENT_WARNING = getattr(settings, 'DOCUMENTS_PARSER_WIKIROLE_SILENT_WARNING', False)

# Reprends la local des settings mais seulement la première partie, le parser ne 
# supportant pas une local de la forme ``xx_XX``
DOCUMENTS_PARSER_LANGUAGE_CODE = getattr(settings, 'LANGUAGE_CODE', "en").split('_')[0]

# Permet d'activer les directives qui permettent d'insérer du HTML/JS/.., désactivé par 
# défaut par sécurité
DOCUMENTS_PARSER_ENABLE_FILE_INSERTION = getattr(settings, 'DOCUMENTS_PARSER_ENABLE_FILE_INSERTION', False)
DOCUMENTS_PARSER_ENABLE_RAW_INSERTION = getattr(settings, 'DOCUMENTS_PARSER_ENABLE_RAW_INSERTION', False)

# Schémas d'options pour le parser dans les settings, ceux définits ici sont ceux par 
# défaut utilisés, il est donc recommandé de ne pas les supprimer mais les modifier.
# Ce sont uniquement les options acceptés par le parser ReST de docutils, pour plus de 
# détails sur les options : http://docutils.sourceforge.net/docs/user/config.html
# (Le writer utilisé est ``html4css1``).
#
# * default: pour les pages
# * short: pour les documents à insérer
DOCUMENTS_PARSER_FILTER_SETTINGS = {
    'default':{
        'initial_header_level': 3,
        'file_insertion_enabled': DOCUMENTS_PARSER_ENABLE_FILE_INSERTION,
        'raw_enabled': DOCUMENTS_PARSER_ENABLE_RAW_INSERTION,
        'language_code': DOCUMENTS_PARSER_LANGUAGE_CODE,
        'footnote_references': 'superscript',
        'doctitle_xform': False,
    },
    'short':{
        'initial_header_level': 3,
        'file_insertion_enabled': DOCUMENTS_PARSER_ENABLE_FILE_INSERTION,
        'raw_enabled': DOCUMENTS_PARSER_ENABLE_RAW_INSERTION,
        'language_code': DOCUMENTS_PARSER_LANGUAGE_CODE,
        'footnote_references': 'superscript',
        'doctitle_xform': False,
    },
}
DOCUMENTS_PARSER_FILTER_SETTINGS.update(getattr(settings, 'DOCUMENTS_PARSER_FILTER_SETTINGS', {}))

# Nom de préfix des class CSS des éléments ajoutés par Pygments
PYGMENTS_CONTAINER_CLASSPREFIX = getattr(settings, 'PYGMENTS_CONTAINER_CLASSPREFIX', "pygments")
# Active l'utilisation de styles insérés directement dans chaque élément HTML généré par 
# Pygment au lieu de l'utilisation de class CSS, désactivé par défaut
PYGMENTS_INLINESTYLES = getattr(settings, 'PYGMENTS_INLINESTYLES', False)

#Clés de cache
PAGE_RENDER_CACHE_KEY_NAME = 'documents-render-page_{id}-setting_{setting}'
INSERT_RENDER_CACHE_KEY_NAME = 'documents-render-insert_{id}-setting_{setting}-hlv_{header_level}'
PAGE_TOC_CACHE_KEY_NAME = 'documents-toc-page_{id}-setting_{setting}'
INSERT_TOC_CACHE_KEY_NAME = 'documents-toc-insert_{id}-setting_{setting}-hlv_{header_level}'
PAGE_SLUGS_CACHE_KEY_NAME = 'documents-page_slugs'
