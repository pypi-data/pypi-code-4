# -*- coding: utf-8 -*-
"""
Template rendering decorator
"""
from functools import wraps
from django.utils.decorators import available_attrs
from django.shortcuts import render_to_response
from django.template import RequestContext


def render_template(template):
    """
    Shortcut for rendering templates with RequestContext

    Simply apply the decorator, and return a dict from your view.

    If decorated function returns non dict then just return that result
    else use RequestContext for rendering the template.

    :param template: Relative path to template file
    :type template:
    :return: Rendered template http response
    :rtype: HttpResponse
    """

    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            else:
                return render_to_response(
                    template,
                    output,
                    context_instance=RequestContext(request)
                )

        return wrapper

    return decorator