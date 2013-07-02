from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.utils import timezone


try:
    from riak import RiakClient, RiakPbcTransport
except ImportError:
    raise ImproperlyConfigured, ("Could not load riak dependency.")


RIAK_DB_HOST = getattr(settings, 'RIAK_DB_HOST', '127.0.0.1')
RIAK_DB_PORT = getattr(settings, 'RIAK_DB_PORT', 8087)
RIAK_DB_BUCKET = getattr(settings, 'RIAK_DB_BUCKET', 'djsessions')


class SessionStore(SessionBase):
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        client = RiakClient(host=RIAK_DB_HOST,
                            port=RIAK_DB_PORT,
                            transport_class=RiakPbcTransport)
        self.sessions = client.bucket(RIAK_DB_BUCKET)

    def exists(self, session_key):
        return self.sessions.get(session_key).exists()


    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if must_create and self.exists(self._get_or_create_session_key()):
            raise CreateError
        data = self.encode(self._get_session(no_load=must_create))
        session_data = self.sessions.new(self._get_or_create_session_key(),
                                         data)
        session_data.set_usermeta({'expire_age': self.get_expiry_date().strftime("%s")})
        session_data.store()

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
        session_data = self.sessions.get(session_key)
        if session_data.exists():
            session_data.delete()

    def load(self):
        session_data = self.sessions.get(self.session_key)
        if session_data.exists() and int(session_data.get_usermeta()['expire_age']) > int(timezone.now().strftime("%s")):
            return self.decode(session_data.get_data())
        else:
            self.create()
            return {}
