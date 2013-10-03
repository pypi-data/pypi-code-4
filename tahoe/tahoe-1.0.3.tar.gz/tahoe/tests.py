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
import base64
from contextlib import contextmanager

from flask.ext.testing import TestCase, ContextVariableDoesNotExist
from nose.plugins.skip import SkipTest
from tahoe.fixtures import FixturesRegistry


def skip(test):
    """ @skip decorator to skip WIP tests """
    def wrapper(*args, **kwargs):
        raise SkipTest()
    wrapper.__name__ = test.__name__
    wrapper.__doc__ = test.__doc__
    return wrapper


def index_db(test):
    def wrapper(self, *args, **kwargs):
        self.reindex_db()
        test(self, *args, **kwargs)
    wrapper.__name__ = test.__name__
    wrapper.__doc__ = test.__doc__
    return wrapper


class TahoeTestCase(TestCase):
    """
    Test harness for the Tahoe application
    """
    TAHOE_APPLICATION = None

    @classmethod
    def register_tahoe_application(cls, tahoe_app):
        cls.TAHOE_APPLICATION = tahoe_app

    def __init__(self, *args, **kwargs):
        self.db = self.tahoe.db
        self.models = self.tahoe.models
        self._fixtures = None
        super(TahoeTestCase, self,).__init__(*args, **kwargs)

    @property
    def tahoe(self):
        return self.TAHOE_APPLICATION

    def create_app(self):
        return self.tahoe.app

    def _pre_setup(self):
        super(TahoeTestCase, self)._pre_setup()
        self.reset_db()

    def _post_teardown(self):
        super(TahoeTestCase, self)._post_teardown()
        self.db.session.close()

    @property
    def fixtures(self):
        if not self._fixtures:
            self._fixtures = FixturesRegistry(
                models=self.models,
                db=self.db)
            self._fixtures.setup()
        return self._fixtures

    @property
    def current_session(self):
        try:
            sess = self.get_context_variable('session')
        except ContextVariableDoesNotExist:
            sess = None
        return sess

    @property
    def logger(self):
        return self.app.logger

    def ppr(self, response, chunk=256, fuzziness=0.1):
        print "Status code: {}".format(response.status_code)
        print "Headers    : {}".format(response.headers)
        print "==============="
        print "Data:"
        if len(response.data) > (chunk * (1.0 + fuzziness)):
            print "{}\n...\n{}\n\n".format(
                response.data[0:(chunk / 2)],
                response.data[-(chunk / 2):])
        else:
            print "{}\n\n".format(response.data)

    def reset_db(self):
        self.db.engine.dispose()
        self.tahoe.drop_all_tables()
        self.tahoe.create_all_tables()
        self.fixtures.load()
        self.tahoe.aws.clear_mock_buckets()

    def reindex_db(self):
        """
        Will create new indexes and index all the data currently in the
        database for the following models. Should only be called when you
        need to start with a blank elasticsearch slate for a test.
        """
        # This shouldn't be hardcoded, right?
        models_to_index = [m for m in self.models.models.values() if hasattr(m, '_search_index_all_records')]
        indices = []
        for model in models_to_index:
            res = model._search_index_all_records(remove_old=True, refresh_now=False)
            indices.append(res['index_name'])
        self.tahoe.elastic_search.refresh(indices)

    def _parse_cookie(self, cookie_data):
        cookie = dict()
        cookie_bits = [pair.split('=') for pair in cookie_data.split('; ')]
        cookie['name'], cookie['value'] = cookie_bits.pop(0)
        for pair in cookie_bits:
            if len(pair) == 0:
                continue
            key = pair[0]
            if len(pair) == 1:
                value = True
            else:
                value = pair[1]
            cookie[key] = value
        cookie_expires = cookie.get('expires')
        if cookie_expires:
            cookie['session'] = False
        else:
            cookie['session'] = True

        if cookie_expires == 'Thu, 01-Jan-1970 00:00:00 GMT' and \
            cookie.get('Max-Age') == '0' and \
                cookie.get('value', '').strip() == '':
                    cookie['destroyed'] = True
        else:
            cookie['destroyed'] = False
        return cookie

    def _parse_cookies(self, response):
        cookies = dict()
        for key, value in response.headers:
            if key == 'Set-Cookie':
                cookie = self._parse_cookie(value)
                cookies[cookie['name']] = cookie
        return cookies

    def _get_cookie(self, response, cookie_name):
        cookies = self._parse_cookies(response)
        return cookies.get(cookie_name)

    def cookieWasSet(self, response, cookie_name, **kwargs):
        cookie = self._get_cookie(response, cookie_name)
        if cookie:
            if kwargs:
                for key, value in kwargs.iteritems():
                    if cookie.get(key) != value:
                        return False
            return True
        return False

    def cookieWasDestroyed(self, response, cookie_name):
        cookie = self._get_cookie(response, cookie_name)
        return cookie and cookie.get('destroyed')

    def assert201(self, response):
        self.assertStatusCode(response, status_code=201)

    def assert209(self, response):
        self.assertStatusCode(response, status_code=209)

    def assertStatusCode(self, response, status_code):
        assert self.isStatusCode(response, status_code)

    def isStatusCode(self, response, status_code):
        return response.status_code == status_code

    def get_json(self, response):
        json = response.json
        return json.get('r')

    @contextmanager
    def config_change(self, key, temp_value):
        old_value = self.app.config.get(key)
        self.logger.debug("Changing config key ({}) from '{}' to \
            '{}'.".format(key, old_value, temp_value))
        self.app.config[key] = temp_value
        yield
        if old_value:
            self.logger.debug("Resetting config key ({}) from '{}' to \
                '{}'.".format(key, temp_value, old_value))
            self.app.config[key] = old_value
        else:
            self.logger.debug("Removing config key ({}).".format(key))
            del self.app.config[key]
