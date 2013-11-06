#!/usr/bin/env python
# Copyright (c) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC>
#
"""Configuration options for template rendering and
parsing.

This class provides a compatibility bridge between customizable 
template backends and the Django ``RequestContext`` object.

TODO: Add support for Genshi templates.
"""
import os
from notmm.utils.template        import TemplateLoaderFactory
from notmm.utils.django_settings import SettingsProxy

__all__ = ('get_template_loader', 'get_app_conf')

_settings = SettingsProxy(autoload=True).get_settings()
_cache_enabled = getattr(_settings, 'ENABLE_BEAKER', False)

class TemplateException(StandardError):
    pass

def get_app_conf(name='development.ini'):

    try:
        from notmm.utils.configparse import loadconf
        rootdir = os.environ['ROOTDIR']
        app_conf = loadconf(name)
    except (ImportError, KeyError):
        app_conf = {}
    return app_conf

# register a default template backend instance 
def get_template_loader():
    TemplateLoaderFactory.configure(
        #backend='mako', 
        #template_loader_class='CachedTemplateLoader',
        kwargs={
            'directories' : _settings.TEMPLATE_DIRS, 
            'cache_enabled':_cache_enabled
            }
    )
    loader = TemplateLoaderFactory.get_loader()
    return loader

