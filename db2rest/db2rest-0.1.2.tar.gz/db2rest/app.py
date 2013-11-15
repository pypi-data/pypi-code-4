"""This modules provide the main class of the application

"""
import os
import sys

import werkzeug.exceptions as ex
from werkzeug.wrappers import Request
from werkzeug.wsgi import SharedDataMiddleware

from db2rest.db import DBAdapter
from db2rest.rest import RestAPI
from db2rest.exceptions import NotFound, Unauthorized
from db2rest.auth import is_authenticated


__all__ = ["DB2Rest", "create_app", "initialize_ldap",
           "create_logger", "start", "create_map"]


class DB2Rest(object):

    def __init__(self, db_engine, host, port, log, ldap):
        self.url_map = create_map(db_engine)
        self.host = host
        self.port = port
        self.log = log
        self.ldap = ldap
        self.db_adapter = DBAdapter(db_engine)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            values['view'] = endpoint
            api = RestAPI(self.db_adapter)
            if is_authenticated(self.ldap, request):
                return getattr(api, request.method.lower())(request, values)
            raise Unauthorized()
        except ex.NotFound, e:
            return NotFound()
        except ex.HTTPException, e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(config_file):
    """Create the app and the db engine given the configuration file
    """
    from sqlalchemy import create_engine
    import ConfigParser

    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    host = config.get('webserver', 'host')
    port = config.getint('webserver', 'port')
    db_engine = create_engine(config.get('db', 'string_connection'))
    log = create_logger(config.get('logger', 'level'))
    ldap = initialize_ldap(config.get('ldap', 'string_connection'),
                           config.get('ldap', 'query'))
    app = DB2Rest(db_engine, host, port, log, ldap)
    shared = SharedDataMiddleware(
        app.wsgi_app,
        {'/static':  os.path.join(os.path.dirname(__file__), 'static')})
    app.wsgi_app = shared
    return app


def initialize_ldap(string_connection, query):
    """Initialize the connection with the LDAP server provided the connection string
    """
    import ldap
    conn = ldap.initialize(string_connection)
    return dict(ldap=conn, query=query)


def create_logger(level):
    """Create the logger for the application given the level
    """
    import logging
    logging.basicConfig(level=logging.getLevelName(level))
    return logging


def create_map(db_engine):
    """Create a map between the database schema and the application
        - Each table in the database will be first level of the hiearachy
        - Each row will be the second level
    """

    from werkzeug.routing import Map, Rule
    from sqlalchemy.schema import MetaData
    meta = MetaData()
    meta.reflect(bind=db_engine)
    rules = [Rule('/', endpoint='Tables')]

    for table in reversed(meta.sorted_tables):
        rules.append(Rule("/%s" % table, endpoint='Table'))
        rules.append(Rule("/%s/<int:id>" % table, endpoint='Row'))
    return Map(rules)


def start():
    """Start the app"""
    from werkzeug.serving import run_simple

    config_file = os.path.join(os.path.dirname(__file__), 'config.cfg')

    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    if not os.path.exists(config_file):
        raise IOError("Cannot read the configuration file:")
    app = create_app(config_file)
    run_simple(app.host, app.port, app, use_debugger=True, use_reloader=True)
