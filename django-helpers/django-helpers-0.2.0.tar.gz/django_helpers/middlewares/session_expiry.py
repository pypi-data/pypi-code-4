# coding=utf-8
from datetime import datetime
from django.http import HttpResponseRedirect
from django_helpers import get_settings_val


SESSION_TIME_OUT = get_settings_val('SESSION_TIME_OUT_INTERVAL', 10 * 60)


class SessionExpiredMiddleware:
    def process_request(self, request):
        """
        @param request: The request object
        @type request: django.http.HttpRequest
        @return:
        """
        session = getattr(request, 'session', None)
        if session is None:
            return None

        last_activity = session.get('last_activity')
        now = datetime.now()
        if last_activity is not None:
            if (now - last_activity).seconds > SESSION_TIME_OUT:
                return HttpResponseRedirect("LOGIN_PAGE_URL")
        session['last_activity'] = now