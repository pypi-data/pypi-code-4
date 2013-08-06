import urlparse
import warnings
import cgi

import db

import psycopg2
import psycopg2.extras
import psycopg2.extensions

Binary = psycopg2.Binary


class Psycopg2Driver(db.drivers.Driver):
    PARAM_STYLE = "pyformat"
    URL_SCHEME = "postgresql"

    def __init__(self, *args, **kwargs):
        self.conn_args = args
        self.conn_kwargs = kwargs

    def setup_cursor(self, cursor):
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, cursor)

    def ignore_exception(self, ex):
        return "no results to fetch" in str(ex)

    def connect(self):
        return self._connect(*self.conn_args, **self.conn_kwargs)

    @staticmethod
    def _connect(*args, **kwargs):
        search_path = kwargs.pop("search_path", None)
        kwargs.setdefault("connection_factory",
                          psycopg2.extras.NamedTupleConnection)
        conn = psycopg2.connect(*args, **kwargs)
        if search_path:
            conn.cursor().execute("SET search_path = %s" % search_path)
        return conn

    @classmethod
    def from_url(cls, url):
        parsed = urlparse.urlparse(url)
        db_name = parsed.path[1:].split("?", 1)[0]
        addl_kwargs = cls._get_kwargs(url)
        if parsed.scheme not in ("postgresql", "postgres"):
            warnings.warn("Parsed scheme '%s' not one of 'postgresql' or 'postgres', strange things may happen: %s" % (parsed.scheme, url))
        return cls(dbname=db_name,
                   user=parsed.username,
                   password=parsed.password,
                   host=parsed.hostname,
                   port=parsed.port or 5432,
                   **addl_kwargs)

    @classmethod
    def _get_kwargs(cls, url):
        url = "http:" + url.split(":", 1)[1]
        query = urlparse.urlparse(url).query
        kwargs = cgi.parse_qs(query)
        return cls.condense_unilists(kwargs)

    @staticmethod
    def condense_unilists(d):
        d = dict(d.iteritems())
        for k, v in d.iteritems():
            if isinstance(v, list) and len(v) == 1:
                d[k] = v[0]
        return d


db.drivers.autoregister_class(Psycopg2Driver)
db.drivers.autoregister_class(Psycopg2Driver, scheme="postgres")

__all__ = ["db", "Psycopg2Driver", "Binary"]
