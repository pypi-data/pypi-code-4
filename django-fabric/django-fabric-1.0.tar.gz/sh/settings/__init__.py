# -*- coding: utf8 -*-
from sh.settings.base import *

try:
    from sh.settings.local import *
except ImportError, e:
    raise ImportError("Couldn't load local settings")

if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    from mocco.settings.debug_toolbar import *
    INSTALLED_APPS += ('debug_toolbar',)