from importlib import import_module

from django.conf import settings
from django.utils import six



def get_backend():
    BACKEND = getattr(settings, 'PROFILING_BACKEND',
        'dprofiling.backends.db.DatabaseBackend')
    if isinstance(BACKEND, six.string_types):
        _module, _class = BACKEND.rsplit('.', 1)
        _module = import_module(_module)

        BACKEND = getattr(_module, _class)

    return BACKEND(**getattr(settings, 'PROFILING_BACKEND_OPTIONS', {}))

