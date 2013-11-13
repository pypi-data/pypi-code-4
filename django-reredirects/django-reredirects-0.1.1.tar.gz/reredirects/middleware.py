from __future__ import unicode_literals
import re

from django.utils.http import urlquote
from django.conf import settings
from django import http

from .models import Redirect


class ReRedirectFallbackMiddleware(object):

    # Defined as class-level attributes to be subclassing-friendly.
    response_gone_class = http.HttpResponseGone
    response_redirect_class = http.HttpResponsePermanentRedirect

    def process_response(self, request, response):
        # No need to check for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        full_path = urlquote(request.get_full_path())

        r = None
        try:
            r = Redirect.objects.get(old_path=full_path)
        except Redirect.DoesNotExist:
            pass
        if settings.APPEND_SLASH and not request.path.endswith('/'):
            # Try appending a trailing slash.
            path_len = len(request.path)
            full_path = full_path[:path_len] + '/' + full_path[path_len:]
            try:
                r = Redirect.objects.get(old_path=full_path)
            except Redirect.DoesNotExist:
                pass

        if not r:
            for redirect in Redirect.objects.filter(old_path__icontains='(').filter(old_path__icontains=')'):
                match = re.search(redirect.old_path, full_path, re.I)
                if match:
                    r = redirect
                    for i, m in enumerate(match.groups()):
                        r.new_path = r.new_path.replace('$%s' % (i + 1), m)

        if r is not None:
            if r.new_path == '':
                return self.response_gone_class()
            # Prevent endless redirects to a relative path
            if not r.new_path.startswith('http') or not r.new_path.startswith('/'):
                r.new_path = "/%s" % r.new_path
            return self.response_redirect_class(r.new_path)

        # No redirect was found. Return the response.
        return response
