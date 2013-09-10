
from . import TestCase


class RootTests(TestCase):
    """
    Test root module.
    """

    def test_includeme(self):
        self.config.include('tailbone')
