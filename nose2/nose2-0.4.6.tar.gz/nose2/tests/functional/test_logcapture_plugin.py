import re

from nose2.tests._common import FunctionalTestCase


class LogCaptureFunctionalTest(FunctionalTestCase):
    def test_package_in_lib(self):
        match = re.compile('>> begin captured logging <<')
        self.assertTestRunOutputMatches(
            self.runIn('scenario/package_in_lib', '--log-capture'),
            stderr=match)
