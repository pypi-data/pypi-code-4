# -*- coding: utf-8 -*-
# Inspired by Django REST Framework's excellent settings handling
from __future__ import unicode_literals
from rest_framework import six

from django.conf import settings
from django.utils import importlib

USER_SETTINGS = getattr(settings, 'NODETREE', None)

DEFAULTS = {
    'DEFAULT_CONTENT_SERIALIZER': 'nodetree.serializers.BaseContentSerializer',
    'DEFAULT_CONTENT_VIEW_SET': 'nodetree.viewsets.BaseContentViewSet',
    'NODE_VIEW_SET': 'nodetree.viewsets.NodeViewSet',
    'NODE_PERMISSIONS': None,
    'BASE_NODE_SERIALIZER': 'nodetree.serializers.BaseNodeSerializer',
    'BASE_UPDATE_NODE_SERIALIZER': 'nodetree.serializers.BaseUpdateNodeSerializer',
    'BASE_CREATE_NODE_SERIALIZER': 'nodetree.serializers.BaseCreateNodeSerializer',
    'DEFAULT_MAX_DEPTH': 0,
    'ANY_KEYWORD': 'any',
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'BASE_NODE_SERIALIZER',
    'BASE_UPDATE_NODE_SERIALIZER',
    'BASE_CREATE_NODE_SERIALIZER',
    'DEFAULT_CONTENT_SERIALIZER',
    'DEFAULT_CONTENT_VIEW_SET',
    'NODE_VIEW_SET',
    'NODE_PERMISSIONS',
)

def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.

    :param val: Value for the given ``setting_name`
    :type val: list or str or unicode

    :param setting_name: Name of the setting parameter
    :type setting_name: str or unicode

    :rtype: *
    """
    if isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


# TODO: Raise more errors

class NodeTreeSettings(object):
    """
    A settings object, that allows NodeTree settings to be accessed as properties.
    For example:

        from nodetree.settings import nodetree_settings
        print nodetree.DEFAULT_CONTENT_SERIALIZER

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.import_strings = import_strings or ()

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid NodeTree setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)

        # Cache the result
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        pass

nodetree_settings = NodeTreeSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)