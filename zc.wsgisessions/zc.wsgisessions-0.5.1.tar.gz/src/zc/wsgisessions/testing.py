import os.path

import bobo
import paste.deploy

import zc.wsgisessions.sessions


here = os.path.realpath(os.path.dirname(__file__))

_app = None

def get_app():
    global _app
    if _app is None:
        _app = paste.deploy.loadapp(
            'config:test.ini',
            name='test' if not TEST_DB_INIT else 'test-shared-db',
            relative_to=here,
            global_conf={'__TEST__': '1'}
            )
    return _app

def reset_app():
    global _app
    _app = None


@bobo.query('/')
def test(bobo_request):
    return 'Hello'


TEST_DB_INIT = False


def initialize_test_database(database):
    if not TEST_DB_INIT:
        zc.wsgisessions.sessions.initialize_database(database)
