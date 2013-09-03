from settings import settings
from importlib import import_module

__all__ = ['get_cache', 'cache']


def get_cache(cache_settings):
    if cache_settings is None:
        return None

    backend = cache_settings.get('backend', None)
    servers = cache_settings.get('servers', None) or ['127.0.0.1:11211']

    if backend:
        path, cls_name = backend.rsplit('.', 1)
        cls = getattr(import_module(path), cls_name)
        return cls(servers)
    return None

cache = get_cache(settings.get('cache', None))
