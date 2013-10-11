
from . import TestCase


class ViewTests(TestCase):
    """
    Test root views module.
    """

    def test_includeme(self):
        self.config.include('tailbone.views')
