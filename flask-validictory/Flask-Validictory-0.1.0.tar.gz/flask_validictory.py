# -*- coding: utf-8 -*-
"""
    flask.ext.validictory
    ---------------------

    This module provides integration between Flask and Validictory. It lets you validate
    json requests against a schema.

    :copyright: (c) 2013 by innerloop.
    :license: MIT, see LICENSE for more details.
"""

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Mark Angrish'
__license__ = 'MIT'
__copyright__ = '(c) 2013 by innerloop'
__all__ = ['Validictory']

from functools import wraps

from validictory import validate, SchemaError
from werkzeug.exceptions import BadRequest, abort
from flask import request

try:
    from flask.json import _json as json
except ImportError:
    from flask import json


def expects_json(schema):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            try:
                request_json = request.get_json()

                if json is None:
                    ValueError('The request MIME type must be \'application/json\'')

                validate(request_json, schema)
            except BadRequest as ex:
                raise ValueError(ex)
            except SchemaError as ex:
                abort(500, ex.message)

            return func(*args, **kwargs)

        return decorated_view

    return wrapper