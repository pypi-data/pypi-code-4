# -*- coding: utf-8 -*-
"""
Javascript response rendering decorator
"""
from functools import wraps
from django.utils.decorators import available_attrs
from django.shortcuts import render_to_response
from django.template import RequestContext


def render_javascript(template):
    """
    Shortcut for rendering javascript from a django view

    Simply apply the decorator, and return a dict from your view.

    :param template: Relative path to template file
    :type template: str
    :return: HTTP Response with appropriate headers
    :rtype: HTTPResponse
    """

    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            return render_to_response(
                template,
                output,
                context_instance=RequestContext(request),
                mimetype="application/javascript"
            )

        return wrapper

    return decorator