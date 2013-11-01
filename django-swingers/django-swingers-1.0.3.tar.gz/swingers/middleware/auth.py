from __future__ import (division, print_function, unicode_literals,
                        absolute_import)
from django.conf import settings
from django import http
from django.utils import timezone

from datetime import timedelta

from swingers.sauth.models import Token
from swingers.models import get_locals

import logging
import re


logger = logging.getLogger("log." + __name__)

try:
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
except AttributeError:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']


def get_exempt_urls():
    exempt_urls = [settings.LOGIN_URL.lstrip('/')]
    if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
        exempt_urls += list(settings.LOGIN_EXEMPT_URLS)
    return exempt_urls


def cors_preflight_response(request, response=None):
    response = response or http.HttpResponse()
    if "HTTP_ORIGIN" in request.META:
        response['Access-Control-Allow-Origin'] = request.META["HTTP_ORIGIN"]
    else:
        response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
    response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
    response['Access-Control-Allow-Credentials'] = "true"
    if 'HTTP_ACCESS_CONTROL_REQUEST_HEADERS' in request.META:
        response['Access-Control-Allow-Headers'] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
    return response


class AuthenticationMiddleware(object):
    def process_request(self, request):
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            return cors_preflight_response(request)
        _locals = get_locals()
        _locals.request = request
        akey = "access_token"

        # Add site name to request object
        request.SITE_NAME = settings.SITE_NAME
        request.footer = " (( {0} {1} ))".format(request.SITE_NAME.split("_")[0], "11.06")

        for key in request.GET.keys():
            if key.lower() == akey:
                akey = key
        if akey in request.GET:
            access_token = request.GET[akey]
        elif "HTTP_ACCESS_TOKEN" in request.META:
            logger.info("Found access token %s" % request.META['HTTP_ACCESS_TOKEN'])
            access_token = request.META["HTTP_ACCESS_TOKEN"]
        else:
            access_token = None
        # if the request is made with a token check auth/magically authenticate
        if access_token is not None and Token.objects.filter(secret=access_token).exists():
            token = Token.objects.get(secret=access_token)
            valid = timezone.now() - timedelta(seconds=token.timeout) < token.modified
            valid = valid or token.timeout == 0
            if valid:
                # set backend to first available and log user in
                token.user.backend = settings.AUTHENTICATION_BACKENDS[0]
                request.user = token.user
                # don't force CSRF checks on token-authed users
                setattr(request, '_dont_enforce_csrf_checks', True)
                logger.info("Currently logged in as %s" % request.user)
                # refresh tokens modified date
                token.modified = timezone.now()
                token.save()
            else:
                token.delete()
                token = False
        else:
            token = False

        # Required user authentication for all views
        # Ignore authenticated tokens
        if not token:
            allow_anonymous = getattr(settings, 'ALLOW_ANONYMOUS_ACCESS',
                                      False)
            # No-brainer: check
            # `django.contrib.auth.middleware.AuthenticationMiddleware` is
            # installed
            assert hasattr(request, 'user')
            # Require user authentication by default, except for any exempt
            # URLs.
            if not allow_anonymous and not request.user.is_authenticated():
                path = request.path_info.lstrip('/')
                if not any(re.match(m, path) for m in get_exempt_urls()):
                    return http.HttpResponseRedirect(settings.LOGIN_URL)

    def process_response(self, request, response):
        return cors_preflight_response(request, response)
