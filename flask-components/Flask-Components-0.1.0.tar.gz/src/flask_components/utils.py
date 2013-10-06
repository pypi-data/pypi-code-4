# -*- coding: utf-8 -*-
from importlib import import_module
import types


__all__ = [
    'find'
]


def find(name, app=None, components=None):
    """
    Discover any named attributes, modules, or packages and coalesces the
    results.

    Looks in any module or package declared in the the 'COMPONENTS' key
    in the application config.

    Order of found results are persisted from the order that the
    component was declared in.

    @param[in] components
        An array of components; overrides any setting in the application
        config.
    """

    if components is None:
        if app is None:
            from flask import current_app as app

        components = app.config.get('COMPONENTS', [])

    items = []
    for key in components:
        # Attempt to import the component and access the specified name
        # as an attribute.
        module = import_module(key)
        item = getattr(module, name, None)

        if item is None:
            # Attempt to import a module or package in the component
            # with the specified name.
            try:
                item = import_module('.'.join((key, name)))

            except ImportError:
                # Assume this component has nothing under the specified name.
                continue

        if isinstance(item, types.ModuleType):
            all_ = getattr(item, '__all__', None)
            if all_:
                item = {n: getattr(item, n) for n in all_}

            else:
                item = vars(item)

        items.append(item)

    return items
