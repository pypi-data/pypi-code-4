# -*- coding: utf-8 -*-

"""

    importer: timezone tests
    ~~~~~~~~~~~~~~~~~~~~~~~~

    this module tests functionality in ``importer``
    related to timezone and time offset computation.

"""

# stdlib
import time
import unittest
import datetime

# importer
from importer import tz
from importer import mix


## TZTests - puts offset calculation functions through their paces.
class TZTests(unittest.TestCase):

    ''' Tests routines related to calculating
        timezone/DST offsets. '''

    def test_exports(self):

        ''' Make sure that all expected module globals are exported
            where they should be. '''

        self.assertTrue(hasattr(tz, 'timezone'))  # test that proxy exists to :py:mod:`pytz`
