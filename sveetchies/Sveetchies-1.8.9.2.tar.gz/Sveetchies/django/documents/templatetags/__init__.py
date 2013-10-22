# -*- coding: utf-8 -*-
from django.core.cache import cache
from Sveetchies.django.documents.parser import SourceParser, extract_toc

def get_render_with_cache(instance, setting_key="default", force_update_cache=False, initial_header_level=None):
    """
    Renvoi le contenu parsé et transformé par le parser
    
    Utilise le système de cache de Django
    """
    cache_key = instance.get_render_cache_key(setting=setting_key, header_level=initial_header_level)
    if force_update_cache or not cache.get(cache_key):
        if not instance.content:
            rendered = ''
        rendered = SourceParser(instance.content, setting_key=setting_key, initial_header_level=initial_header_level)
        cache.set(cache_key, rendered)
        return rendered
    return cache.get(cache_key)

def get_toc_with_cache(instance, setting_key="default", force_update_cache=False, initial_header_level=None):
    """
    Renvoi le TOC (sommaire) extrait du rendu
    
    Utilise le système de cache de Django
    """
    cache_key = instance.get_toc_cache_key(setting=setting_key, header_level=initial_header_level)
    if force_update_cache or not cache.get(cache_key):
        if not instance.content:
            toc = ''
        toc = extract_toc(instance.content, setting_key=setting_key, initial_header_level=initial_header_level)
        cache.set(cache_key, toc)
        return toc
    return cache.get(cache_key)
