"""Misc template backends and utilities"""
from notmm.utils.configparse import string_getter

__all__ = [
    'available_backends',
    'TemplateLoaderFactory',] 

class TemplateLoaderFactory(object):
    """A proxy class which delegates access to a template loader instance"""

    loader_instance = None

    def __init__(self, label=''):
        self._label = label # Backend name (optional)

    def __call__(self, **kwargs):
        return getattr(self, 'loader_instance').__call__(**kwargs)

    def __repr__(self):
        return "<TemplateLoaderFactory: %s>" % self.get_loader()

    @classmethod
    def get_loader(cls):
        """Returns the currently defined template
        loader backend instance."""

        return getattr(cls, 'loader_instance')
    
    @classmethod
    def set_loader(cls, attr, value):
        """Set the class ``loader_instance`` attribute, 
        or raise an exception if loader is invalid/unusable."""
        setattr(cls, attr, value)
        return None

    @classmethod
    def configure(cls, 
    backend='mako',
    template_loader_class='CachedTemplateLoader',
    kwargs={}):
        """
        Setup a default template_loader instance for template loading and 
        rendering. Such an inheritable object should have a ``get_template`` 
        method for properly looking up templates. 
        """
        # 'mako.CachedTemplateLoader' -> notmm.utils.template.backend.i
        import notmm.utils.template.backends as mod
        try:
            instance = getattr(getattr(mod, backend), template_loader_class).__call__(**kwargs)
        except Exception:
            raise
        else:
            cls.set_loader('loader_instance', instance)
        return None

available_backends = {
    'mako': TemplateLoaderFactory(label='Mako 0.8.1')
}

if __name__ == '__main__':
    print "available backends:"
    for backend in available_backends:
        print backend
