"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature


class ItsdangerousSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.modified = False


class ItsdangerousSessionInterface(SessionInterface):
    DEFAULT_SALT = 'session-salt'
    session_class = ItsdangerousSession

    def __init__(self, *args, **kwargs):
        super(ItsdangerousSessionInterface, self).__init__()
        self.config = kwargs.get('config')
        self._salt = None

    @property
    def salt(self):
        if not self._salt:
            self._salt = self.config.get('SESSION_SALT', self.DEFAULT_SALT)
        return self._salt

    def get_serializer(self, app):
        if not app.secret_key:
            return None

        return URLSafeTimedSerializer(app.secret_key,
                                      salt=self.salt)

    def open_session(self, app, request):
        s = self.get_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(app.session_cookie_name)
        if not val:
            return self.session_class()
        max_age = app.permanent_session_lifetime.total_seconds()
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if session.modified and not session:
            response.delete_cookie(app.session_cookie_name,
                                   domain=domain
                                   )
        else:
            val = self.get_serializer(app).dumps(dict(session))
            response.set_cookie(app.session_cookie_name, val,
                                expires=None, httponly=True,
                                domain=domain)
