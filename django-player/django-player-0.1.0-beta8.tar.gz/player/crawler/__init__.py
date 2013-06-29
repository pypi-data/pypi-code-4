from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def get_backend(backend_mod_name):
    """ Returns crawler backend """
    try:
        backend = import_module(backend_mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing crawler backend module %s: "%s"'
                                    % (backend_mod_name, e)))
    return backend


def get_backends():
    """ Returns all crawler backends """
    return settings.CRAWLER_BACKENDS
