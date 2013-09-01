
import datetime

from . import TestCase
from tailbone import helpers


class HelpersTests(TestCase):

    def test_pretty_date(self):
        helpers.pretty_date(datetime.date(2013, 6, 19))
