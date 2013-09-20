# -*- coding: utf-8 -*-
"""
P3P Policy header injection middleware
"""
from django.conf import settings

DEFAULT_P3P_COMPACT = 'CP="NOI ADM DEV PSAi NAV OUR STP IND DEM"'


class NPResponseInjectP3PMiddleware(object):
    """
    Inject P3P headers so that IE will accept third party cookies from iframes

    Note that for IE9 this has to be a valid value - gone are the days where
    you can fill it in with nonsense.
    """

    def __init__(self):
        self.process_response = self.inject_p3p_header

    def inject_p3p_header(self, request, response):
        """
        Inject P3P headers so that IE will accept third party cookies from an
        iframe.

        :param request: Django request object
        :type request: HttpRequest
        :param response: Django response object
        :type response: HttpResponse
        :return: Response object with added P3P header
        :rtype: HttpResponse
        """

        if hasattr(settings, 'P3P_COMPACT'):
            response['P3P'] = settings.P3P_COMPACT
        else:
            response['P3P'] = DEFAULT_P3P_COMPACT

        return response
