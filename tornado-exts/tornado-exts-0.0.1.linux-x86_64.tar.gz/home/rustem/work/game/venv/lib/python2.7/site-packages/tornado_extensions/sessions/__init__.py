from settings import settings
from importlib import import_module

__all__ = ['get_engine', 'engine']


def get_engine(session_settings):
    if session_settings is None:
        return None

    backend = session_settings.get('engine', None)

    if backend:
        mod = import_module(backend)
        # stupid monkey patch
        mod.SessionStore.settings = session_settings
        return mod
    return None

engine = get_engine(settings.get('django_session', None))
