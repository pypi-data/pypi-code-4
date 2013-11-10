# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# Django imports.
from django import template
from django.core import urlresolvers


# Get an instance of Django's template library.
register = template.Library()


@register.simple_tag(takes_context=False)
def html_link(text, view, *args, **kwargs):
    """
    A small wrapper for showing HTML links.

    Positional arguments:

        text - Text that should be used as a link.

        view - View name for which the URL should be shown

        args - Additional positional arguments that will be passed to resolver
        for creating the URL.

    Keyword arguments:

        id - Identifier for the <a> HTML element.

        class - Class(es) for the <a> HTML element.

        title - Title for the HTML <a> element.

        get - Additional GET parameter that should be appended to the URL.

    """

    # Generate the URL by using the supplied view name and arguments that should
    # be passed to the view.
    url = urlresolvers.reverse(view, args=args)

    # Set-up the base pattern (url, parameters, text).
    pattern = '<a href="%s" %s>%s</a>'

    # Iterate over keyword arguments, and if they're supported, add them to
    # parameters.
    params = ""
    for key, value in kwargs.iteritems():
        if key in ("class", "title", "id"):
            params += '%s="%s" ' % (key, value)
        elif key == "get":
            url += "?%s" % value
        else:
            raise template.TemplateSyntaxError("Unknown argument for 'advhtml_link' tag: %r" % key)

    # Render the tag.
    return pattern % (url, params, text)


@register.simple_tag(takes_context=True)
def active_link(context, url_name, return_value='active', **kwargs):
    """
    This template tag can be used to check if the provided URL matches against
    the path from the request or not.

    Arguments:

      context - Context of the current view being called.

      url_name - Name of the URL that's being checked against current path from
      request.
    """

    matches = current_url_equals(context, url_name, **kwargs)

    return return_value if matches else ''


def current_url_equals(context, url_name, **kwargs):
    """
    Helper function for checking if the specified URL corresponds to the current
    request path in the context.

    Arguments:

      - context - Context of the view being rendered.

      - url_name - Name of the URL against which the context request path is
      being checked.
    """

    # Assume that we have not been able to resolve the request path to an URL.
    resolved = False
    try:
        # Use the request path, and resolve it to a URL name.
        resolved = urlresolvers.resolve(context.get('request').path)
    except urlresolvers.Resolver404:
        # This means we haven't been able to resolve the path from request.
        pass

    # If the request was resolved and URL names match, verify that the kwargs
    # match as well.
    matches = resolved and resolved.url_name == url_name
    if matches and kwargs:
        for key in kwargs:
            kwarg = kwargs.get(key)
            resolved_kwarg = resolved.kwargs.get(key)
            if not resolved_kwarg or kwarg != resolved_kwarg:
                return False

    return matches
