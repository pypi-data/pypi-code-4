# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from functools import partial
import armet


def _get_config(store, application, key, default=None):
    name = 'ARMET_%s' % key.upper()
    if name in application.config:
        store[key] = application.config[name]

    elif default is not None:
        store[key] = default


def configure(application):
    # Gather configuration from the application config.
    store = {}
    get = partial(_get_config, store, application)
    get('debug', default=False)
    connector = 'alchemist_armet'
    get('connectors', default={'http': connector, 'model': connector})
    get('trailing_slash', default=True)
    get('http_exposed_headers')
    get('http_allowed_origins')
    get('legacy_redirect')
    get('serializers')
    get('allowed_serializers')
    get('default_serializer')
    get('deserializers')
    get('allowed_deserializers')
    get('authentication')
    get('authorization')

    # Apply configuration.
    armet.use(**store)
