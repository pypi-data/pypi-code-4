from types import StringTypes


def autodiscover(*names):
    """
    borrowed from django admin.
    """
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        for name in names:
            if type(name) not in StringTypes:
                raise
            try:
                import_module('%s.%s' % (app, name))
            except:
                if module_has_submodule(mod, name):
                    raise