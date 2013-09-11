
from mock import Mock

from . import TestCase
from tailbone import subscribers


class SubscribersTests(TestCase):

    def test_before_render(self):
        event = Mock()
        event.__setitem__ = Mock()
        subscribers.before_render(event)
