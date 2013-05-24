#from django.core.cache import cache
from django.core.cache import get_cache

from django.db.models.signals import post_save, post_delete
from httplib import HTTPConnection
from django.conf import settings


def cache_invalidator(sender, **kwargs):

    if hasattr(settings, 'O2W_CACHE_INVALIDATOR'):
        # Borramos la cache de objectos
        cache = get_cache('default')
        cache.clear()
            
        # Ahora borrramos la cache del middleware
        cache = get_cache(settings.CACHE_MIDDLEWARE_ALIAS)
        cache.clear()            
                
        # purgamos la cache de varnish             
        varnish = settings.O2W_CACHE_INVALIDATOR['varnish']
        domain = settings.O2W_CACHE_INVALIDATOR['domain']
        HTTPConnection(varnish, 80).request('PURGE', '/.*', '', {'Host': domain }) 



post_save.connect(cache_invalidator)
post_delete.connect(cache_invalidator)
