from flask.sessions import SessionInterface, SessionMixin
from kyototycoon import KyotoTycoon, KT_DEFAULT_PORT, KT_DEFAULT_HOST
from werkzeug.datastructures import CallbackDict
from httplib import BadStatusLine

from datetime import datetime
from uuid import uuid4


class KyotoTycoonSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        super(KyotoTycoonSession, self).__init__(initial)
        self.sid = sid
        self.modified = False
        self.permanent = True

class KyotoTycoonSessionInterface(SessionInterface):
    def __init__(self, host=KT_DEFAULT_HOST, port=KT_DEFAULT_PORT):
        connection = KyotoTycoon()
        connection.open(host, port)
        self.connection = connection
        self.host = host
        self.port = port

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            stored_session = None
            try:
                stored_session = self.connection.get(sid, db=app.name)
            except BadStatusLine:
                connection = KyotoTycoon()
                connection.open(self.host, self.port)
                self.connection = connection
                stored_session = self.connection.get(sid, db=app.name)

            if stored_session:
                return KyotoTycoonSession(initial=stored_session['data'],
                    sid=stored_session['sid'])
        sid = unicode(uuid4())
        return KyotoTycoonSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        expiration = self.get_expiration_time(app, session)
        if not expiration:
            # KyotoTycoon has an expiration mechanism that does
            # int(time.time()) + expiration
            expiration = (60 * 60 * 24) # 24 hours
        else:
            # We need to translate self.get_expiration_time into
            # something KyotoTycoon expects
            expiration = int(app.config["PERMANENT_SESSION_LIFETIME"].total_seconds())

        self.connection.set(session.sid,
            { "sid": session.sid
            , "data": session
            },
            expiration,
            db=app.name
        )
        response.set_cookie(app.session_cookie_name, session.sid,
            expires=self.get_expiration_time(app, session),
            httponly=True, domain=domain)
