import doctest
import re
import unittest

import transaction
import zc.dbconnection
import zope.component
import zope.component.testing
import zope.testing.renormalizing
import zope.testing.setupstack

import zc.wsgisessions.testing


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r' at -?0x[^>]+'), ' at 0xc0defeed'),
    ])


def setUp(test):
    zope.testing.setupstack.register(test, zope.component.testing.tearDown)
    zope.component.testing.setUp(test)
    zope.testing.setupstack.register(test, zc.wsgisessions.testing.reset_app)
    app = zc.wsgisessions.testing.get_app()
    test.globs['app'] = app
    conn = test.globs['conn'] = app.database.open()
    zc.dbconnection.set_local(conn)
    zope.testing.setupstack.register(test, test.globs['conn'].close)
    zope.testing.setupstack.register(test, transaction.abort)
    zope.testing.setupstack.register(test, test.globs.pop, 'conn')
    zope.component.provideAdapter(zc.wsgisessions.sessions.get_session)
    # Either this or the one in tearDown is not needed.
    # zope.testing.setupstack.register(test, zc.dbconnection.reset)
    # It seems to work fine without explicit commit
    # transaction.commit()


def setUpWithoutDB(test):
    zope.testing.setupstack.register(
        test, setattr, zc.wsgisessions.testing, 'TEST_DB_INIT', False)
    zc.wsgisessions.testing.TEST_DB_INIT = True
    setUp(test)


def tearDown(test):
    zope.testing.setupstack.tearDown(test)
    zc.dbconnection.reset()


def test_suite():
    optionflags = (
        doctest.NORMALIZE_WHITESPACE |
        doctest.ELLIPSIS |
        doctest.REPORT_NDIFF |
        doctest.REPORT_ONLY_FIRST_FAILURE
        )
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'sessions.txt',
            checker=checker,
            optionflags=optionflags,
            setUp=setUp,
            tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'sessions.txt',
            checker=checker,
            optionflags=optionflags,
            setUp=setUpWithoutDB,
            tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'utils.txt',
            optionflags=optionflags,
            ),
        ))
    return suite
