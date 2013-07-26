# -*- coding: utf-8 -*-
"""
Calcul automatique du chemin d'accès ou chemin de parcours dans les 
urls (aka: breadcrumbs ou pathline)

Ex: Accueil > Mon appli > Ma vue

Voir le ``context_processors`` pour plus de détails.
"""
from django.conf import settings

# Utilisés uniquement par le tag ``{% autobreadcrumbs_links %}``
AUTOBREADCRUMBS_HTML_LINK = getattr(settings, 'AUTOBREADCRUMBS_HTML_LINK', u'<a href="/{link}">{title}</a>')
AUTOBREADCRUMBS_HTML_SEPARATOR = getattr(settings, 'AUTOBREADCRUMBS_HTML_SEPARATOR', u' &gt; ')
