from unittest import TestCase, skip
from pickle import load, dumps
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO
from .package import Package, Version
from .api import PyPI
from .errors import DoesNotExists


class VersionTest(TestCase):

    def setUp(self):
        self.pkg_1 = Version('1.4.5')
        self.pkg_2 = Version('1.5.1')

    def test_repr(self):
        self.assertEqual(repr(self.pkg_1), '1.4.5')

    def test_eq(self):
        self.assertFalse(self.pkg_1 == self.pkg_2)

    def test_eq_str(self):
        self.assertFalse(self.pkg_1 == '1.5.1')

    def test_nq(self):
        self.assertTrue(self.pkg_1 != self.pkg_2)

    def test_nq_str(self):
        self.assertTrue(self.pkg_1 != '1.5.1')

    def test_lt(self):
        self.assertTrue(self.pkg_1 < self.pkg_2)

    def test_lt_str(self):
        self.assertTrue(self.pkg_1 < '1.5.1')

    def test_gt(self):
        self.assertFalse(self.pkg_1 > self.pkg_2)

    def test_gt_str(self):
        self.assertFalse(self.pkg_1 > '1.5.1')

    def test_le(self):
        self.assertTrue(self.pkg_1 <= self.pkg_2)

    def test_le_str(self):
        self.assertTrue(self.pkg_1 <= '1.5.1')

    def test_ge(self):
        self.assertTrue(self.pkg_2 >= self.pkg_1)

    def test_ge_str(self):
        self.assertTrue(self.pkg_2 >= '1.4.5')


class PackagesTest(TestCase):

    def setUp(self):
        self.pkg_1 = Package('Django', '1.4.5', client=None)
        self.pkg_2 = Package('Django', '1.5.1', client=None)

    def test_eq(self):
        self.assertFalse(self.pkg_1 == self.pkg_2)
        self.assertTrue(self.pkg_1 == self.pkg_1)

    def test_nq(self):
        self.assertTrue(self.pkg_1 != self.pkg_2)
        self.assertFalse(self.pkg_2 != self.pkg_2)

    def test_dict(self):
        package = Package('Django', '1.5.1')
        result = dict(package)
        self.assertEqual(result['name'], 'Django')
        self.assertEqual(result['version'], '1.5.1')

    def test_releases(self):
        client = PyPI()
        package = client.get('django')
        self.assertTrue(len(package.releases) > 0)

    def test_metadata(self):
        client = PyPI()
        package = client.get('flask')
        metadata = package.metadata
        self.assertEqual(metadata.author, 'Armin Ronacher')

    def test_release_urls(self):
        client = PyPI()
        package = client.get('django')
        info = package.downloads
        self.assertTrue(info.downloads > 0)
        self.assertTrue(info.size > 10)

    def test_repr(self):
        self.assertEqual(repr(self.pkg_1), 'Django(1.4.5)')


class PyPIClientTest(TestCase):

    def setUp(self):
        self.client = PyPI()
        self.pkg_1 = Package('django', '1.4.5')
        self.pkg_2 = Package('django', '1.5.1')

    def test_packages(self):
        packages = self.client.packages
        try:
            package = next(packages)
        except:
            package = packages.next()
        self.assertTrue(package.name)
        self.assertTrue(package.version > '0.0.1')

    def test_blank_packages(self):
        client = PyPI()
        client.blank_packages = True
        packages = client.packages
        try:
            package = next(packages)
        except:
            package = packages.next()
        try:
            self.assertEqual(type(package), str)
        except AssertionError:
            self.assertEqual(type(package), bytes)

    def test_get(self):
        package = self.client.get('django')
        self.assertEqual(package.name, 'Django')
        self.assertTrue(package.version > self.pkg_1.version)
        self.assertTrue(len(package.releases) > 0)

    def test_search(self):
        packages = self.client.search(name='pulpitum')
        self.assertTrue(len(list(packages)) == 1)

    def test_search_with_fetch_releases(self):
        packages = self.client.search(name='pulpitum')
        packages = list(packages)
        self.assertTrue(len(packages) > 0)
        self.assertTrue(type(packages[0].releases), list)

    def test_invalid_pkg(self):
        with self.assertRaises(DoesNotExists):
            package = self.client.get('basjdais')

    def test_pickling(self):
        flask = self.client.get('flask')
        package = dumps(flask)
        try:
            self.assertEqual(type(package), str)
        except AssertionError:
            self.assertEqual(type(package), bytes)
        try:
            flask = load(StringIO(package))
        except NameError:
            flask = load(BytesIO(package))
        self.assertEqual(flask.name, 'Flask')
        self.assertEqual(flask.version, '0.10.1')
