from pkgtools.pypi import PyPIXmlRpc, real_name
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError
from .package import Package, Version
from .errors import DoesNotExists


class PyPI(object):

    blank_packages = False

    def __init__(self, index_url=None):
        self.client = PyPIXmlRpc(
            index_url=index_url or 'https://pypi.python.org/pypi')

    def get(self, name, version=None):
        try:
            name = real_name(name)
        except HTTPError as error:
            if error.code == 404:
                raise DoesNotExists
            else:
                raise error
        package = Package(name, version, client=self.client)
        return package

    @property
    def packages(self):
        """
        TODO: use yield from construction
        """
        packages = self.client.list_packages()
        for name in packages:
            try:
                if not self.blank_packages:
                    package = Package(name)
                else:
                    package = name
                yield package
            except DoesNotExists:
                pass

    def search(self, **kwargs):
        for package in self.client.search(kwargs):
            name, version, summary = package['name'], package['version'], package['summary']
            package = Package(name, version)
            package.summary = summary
            yield package
