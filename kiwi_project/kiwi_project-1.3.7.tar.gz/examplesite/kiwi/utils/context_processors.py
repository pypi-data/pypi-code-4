# -*- coding: utf-8 -*-
from os.path import join as os_path_join
from django.conf import settings

from Sveetchies.django.context_processors import site_urls as base_site_urls

from kiwi import KIWI_MEDIA_PREFIX
from kiwi import __version__ as kiwi_version

def site_urls(request, extra={}, extra_metas={}):
    """
    Rajoute au context les urls communes à l'applis
    """
    extra_context_metas = {
        'kiwi_version' : kiwi_version,
        'kiwimedias_url' : os_path_join(settings.MEDIA_URL, KIWI_MEDIA_PREFIX),
    }
    extra_context_metas.update(extra_metas)
    
    context = base_site_urls(
        request, 
        extra_metas=extra_context_metas,
    )
    context.update(extra)
    
    return context
