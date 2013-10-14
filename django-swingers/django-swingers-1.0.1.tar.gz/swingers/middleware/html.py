from django.conf import settings

from htmlmin.middleware import (HtmlMinifyMiddleware as
                                DefaultHtmlMinifyMiddleware)

import logging

logger = logging.getLogger("log." + __name__)


class HtmlMinifyMiddleware(DefaultHtmlMinifyMiddleware):
    def can_minify_response(self, request, response):
        # don't minify when debug_toolbar is shown
        DEBUG_TOOLBAR_CONFIG = getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {})
        show_debug_toolbar = DEBUG_TOOLBAR_CONFIG.get('SHOW_TOOLBAR_CALLBACK',
                                                      lambda x: False)

        return (not show_debug_toolbar(request) and
                super(HtmlMinifyMiddleware, self).can_minify_response(
                    request, response))
