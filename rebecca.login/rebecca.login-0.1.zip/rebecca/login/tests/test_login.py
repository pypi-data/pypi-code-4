import unittest
from testfixtures import compare
from pyramid import testing


class TestLogin(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from rebecca.login import login
        return login(*args, **kwargs)

    def test_no_user(self):
        from rebecca.repository import IRepository
        request = testing.DummyRequest()

        users = dict()
        request.registry.registerUtility(users, IRepository, name="users")

        user_name = "testing"
        password = "secret"
        result = self._callFUT(request, user_name, password)
        compare(result, None)

    def test_invalid_password(self):
        from rebecca.repository import IRepository
        request = testing.DummyRequest()

        users = dict(testing=DummyUser("secret"))
        request.registry.registerUtility(users, IRepository, name="users")

        user_name = "testing"
        password = "invalid"
        result = self._callFUT(request, user_name, password)
        compare(result, None)

    def test_it(self):
        from rebecca.repository import IRepository
        request = testing.DummyRequest()

        users = dict(testing=DummyUser("secret"))
        request.registry.registerUtility(users, IRepository, name="users")

        user_name = "testing"
        password = "secret"
        result = self._callFUT(request, user_name, password)
        compare(result, user_name)


class DummyUser(object):
    def __init__(self, password):
        self.password = password

    def validate_password(self, password):
        return self.password == password
