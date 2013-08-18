import unittest

import yolk.yolklib


class TestYolkLib (unittest.TestCase):

    def test_get_highest_version(self):
        versions = [
            '2.2',
            '3.0.5',
            '1.3',
            '3.1.2',
            '1.3.4',
            '0.3',
            '3.1.1',
            '1.2.4']

        self.assertEqual('3.1.2', yolk.yolklib.get_highest_version(versions))

    def test_get_highest_version_with_strange_versions(self):
        versions = [
            '2013.06.25',
            '2013.04.01',
            '2013.07.31',
            '2013.06.31',
            '2013.04.01',
            '2012.09.30',
            '2013.06.31']

        self.assertEqual('2013.07.31',
                         yolk.yolklib.get_highest_version(versions))
