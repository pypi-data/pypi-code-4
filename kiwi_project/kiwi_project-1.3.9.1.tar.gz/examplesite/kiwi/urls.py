# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
#from kiwi.models import Wikipage

urlpatterns = patterns('',
    url(r'^$', 'kiwi.views.wikipage.sitemap', name="kiwi-sitemap"),
    
    # Page de résultats de recherche
    url(r'^search/$', 'kiwi.views.wikipage.search', name="kiwi-search"),
    
    # Page de résultats de recherche
    url(r'^syntax/$', 'kiwi.views.syntax.help', name="kiwi-syntax-help"),
    
    # Page de résultats de prévisualisation d'un text formaté par le parser
    url(r'^syntax/preview/$', 'kiwi.views.syntax.preview', name="kiwi-syntax-preview"),
    
    # Page de résultats de prévisualisation d'une wikipage avec son contexte complet (
    # pour la prévisualisation du BOF Editor dans l'admin)
    url(r'^syntax/preview/(?P<uri>[-\w]+)/$', 'kiwi.views.syntax.wikipage_preview', name="kiwi-syntax-wikipage-preview"),
    #url(r'^admin/wikipage/(?P<instance_id>\d+)/preview/$', 'Sveetchies.django.pywiki2xhtml.views.model_object_preview', kwargs={'model_object': Wikipage}, name="kiwi-syntax-wikipage-preview"),
    
    # Match des uri des pages wiki
    url(r'^(?P<uri>[-\w]+)/$', 'kiwi.views.wikipage.details', name="kiwi-wikipage-details"),
    
    # Historique d'une page
    url(r'^(?P<uri>[-\w]+)/history/$', 'kiwi.views.version.history', name="kiwi-version-history"),
    # Détails d'une version d'une page
    url(r'^(?P<uri>[-\w]+)/history/(?P<version_id>\d+)/$', 'kiwi.views.version.details', name="kiwi-version-details"),
    # Différence entre une version d'une page et celle actuelle
    url(r'^(?P<uri>[-\w]+)/history/(?P<version_id>\d+)/diff/$', 'kiwi.views.version.diff', name="kiwi-version-diff"),
)
