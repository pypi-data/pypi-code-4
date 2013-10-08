# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from django.conf import settings

logger = logging.getLogger(__name__)

max_delta = timedelta(0, getattr(settings, 'REQUEST_MAX_DELTA', 1))


class RequestTimeLoggingMiddleware(object):

    def process_request(self, request):
        request.META['START'] = datetime.now()

    def process_response(self, request, response):
        status = getattr(response, 'status_code', 0)

        str_s = str(status)

        if status in (300, 301, 302, 307):
            str_s += ' => %s' % response.get('Location', '?')
        elif getattr(response, 'content', None):
            str_s += ' %s(%db)' % (request.method, len(response.content))

        try:
            start = request.META['START']
        except:
            return response

        delta = datetime.now() - start
        if delta > max_delta:
            message = u'%s %s секунд %s' % (request.path, delta.seconds, str_s)
            logger.warning(message)
        return response
