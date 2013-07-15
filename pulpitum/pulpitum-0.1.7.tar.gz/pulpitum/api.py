from pkgtools.pypi import PyPIXmlRpc, real_name
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError
from .package import Package, Version
from .errors import DoesNotExists


class PyPI(object):

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
        version = version or self.last_release(name)
        package = Package(name, version, client=self.client)
        package.releases = self.releases(name)
        if version not in package.releases:
            raise DoesNotExists
        else:
            return package

    @property
    def packages(self):
        packages = self.client.list_packages()
        for name in packages:
            package = Package(name, self.last_release(name))
            yield package

    def search(self,  releases=False, **kwargs):
        for package in self.client.search(kwargs):
            name, version = package['name'], package['version']
            package = Package(name, version)
            if releases:
                package.releases = self.releases(name)
            yield package

    def releases(self, name):
        return self.client.package_releases(name)

    def last_release(self, name):
        releases = self.releases(name)
        return releases[0]
