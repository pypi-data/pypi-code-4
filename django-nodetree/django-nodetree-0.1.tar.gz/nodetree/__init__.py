# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nodetree.apps import app
from nodetree.nodetypes import NodeType


def autodiscover():
    """
    A simple clone of the ``django.contrib.admin.autodiscover`` method.

    The original docstring with adjusted NodeTree names:
    Auto-discover INSTALLED_APPS nodetypes.py modules and fail silently when
    not present. This forces an import on them to register any NodeTree bits they
    may want.
    """
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for module in settings.INSTALLED_APPS:
        mod = import_module(module)
        # Attempt to import the module's nodetypes module.
        try:
            before_import_map = copy.copy(app._map._map)
            import_module('%s.nodetypes' % module)
        except:
            app._map._map = before_import_map
            if module_has_submodule(mod, 'nodetypes'):
                raise