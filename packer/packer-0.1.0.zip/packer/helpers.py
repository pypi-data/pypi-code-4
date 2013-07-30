import collections


PackageTuple = collections.namedtuple('PackageTuple', ['name'])

class Package(PackageTuple):

    def __str__(self):
        return '{}'.format(self.name)