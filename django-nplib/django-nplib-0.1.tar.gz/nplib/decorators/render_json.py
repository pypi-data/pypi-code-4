# -*- coding: utf-8 -*-
"""
JSON response rendering decorator
"""
from collections import Iterable
from functools import wraps
from django.utils.decorators import available_attrs
from django.http import HttpResponse
from django.core import serializers
import json


def render_json(not_models=False, mime_type='application/json', status=200):
    """
    Shortcut for rendering JSON from a view

    Simply apply the decorator, and return a dict from your view.

    :param not_models: Switch to inbuilt JSON serializer if no models are
    included in the payload
    :type not_models: bool
    :param mime_type: The mimetype to return the json payload with
    :type mime_type: str
    :param status: The HTTP status code to return the payload with
    :type status: int
    :return: HTTP Response
    :rtype: HttpResponse
    """

    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not_models:
                return HttpResponse(
                    json.dumps(output),
                    mimetype=mime_type,
                    status=status
                )
            else:
                if not isinstance(output, Iterable):
                    output = [output]

                if isinstance(output, dict):
                    data = json.dumps(output)
                else:
                    data = serializers.serialize('json', output)

                return HttpResponse(
                    data,
                    mimetype=mime_type,
                    status=status
                )

        return wrapper

    return decorator