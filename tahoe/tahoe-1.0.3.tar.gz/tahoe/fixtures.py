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
from fixture import SQLAlchemyFixture


class FixturesRegistry(object):
    fixture_callbacks = []
    fixtures = {}

    def __init__(self, models, db):
        self.models = models
        self.db = db
        self._data = None
        self._dbfixture = None

    @classmethod
    def register(cls, name):
        def inner(callback):
            cls.fixture_callbacks.append((name, callback))
        return inner

    def setup(self):
        for fixture_name, fixture_callback in self.fixture_callbacks:
            fixture_class = fixture_callback(
                fixtures=self,
                models=self.models
                )
            self.fixtures[fixture_name] = fixture_class

    def load(self):
        self.data.setup()
        self.dispose()

    def dispose(self):
        self.dbfixture.dispose()

    @property
    def data(self):
        if not self._data:
            # Maintain the order these were imported in.
            fixture_classes = [self.fixtures.get(fixture_name)
                               for fixture_name, fixture_callback
                               in self.fixture_callbacks]
            self._data = self.dbfixture.data(*fixture_classes)
        return self._data

    @property
    def dbfixture(self):
        if not self._dbfixture:
            self._dbfixture = SQLAlchemyFixture(
                env=self.fixture_environment,
                engine=self.db.engine)
        return self._dbfixture

    @property
    def fixture_environment(self):
        env = dict()
        for fixture_name, fixture_class in self.fixtures.iteritems():
            env[fixture_class.__name__] = fixture_class.__model__
        return env

    def get_fixtures(self, fixture_name):
        return self.fixtures.get(fixture_name)

    def __getattr__(self, key):
            return self.get_fixtures(key)

    def __repr__(self):
        return u"<FixturesRegistry fixtures='{}' />".format(self.fixtures.keys())
