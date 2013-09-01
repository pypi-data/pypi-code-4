"""Utility classes, functions etc."""

import sys

import six


class Version(object):

    """Python version numbers with sensible comparisons."""

    def __init__(self, version=sys.version_info[:3]):
        if version in ("inf", float("inf")):
            self.info = (float("inf"),)
        elif isinstance(version, (int, float)):
            self.info = tuple(int(x) for x in str(version).split("."))
        elif isinstance(version, six.string_types):
            self.info = tuple(int(x) for x in version.split(".")[:3])
        elif isinstance(version, Version):
            self.info = version.info
        else:
            self.info = tuple(version)[:3]

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.truncate(other) == other.truncate(self)
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, Version):
            return self.truncate(other) >= other.truncate(self)
        else:
            raise TypeError("unorderable types")

    def __gt__(self, other):
        if isinstance(other, Version):
            return self.truncate(other) > other.truncate(self)
        else:
            raise TypeError("unorderable types")

    def __le__(self, other):
        if isinstance(other, Version):
            return self.truncate(other) <= other.truncate(self)
        else:
            raise TypeError("unorderable types")

    def __lt__(self, other):
        if isinstance(other, Version):
            return self.truncate(other) < other.truncate(self)
        else:
            raise TypeError("unorderable types")

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, str(self))

    def __str__(self):
        return ".".join(str(x) for x in self.info)

    @property
    def major(self):
        """Major version number."""
        return self.info[0]

    @property
    def minor(self):
        """Minor version number."""
        try:
            return self.info[1]
        except IndexError:
            return None

    @property
    def micro(self):
        """Micro version number."""
        try:
            return self.info[2]
        except IndexError:
            return None

    def truncate(self, other):
        """Return `self.info` truncated to the length of `other.info`."""
        return self.info[:len(other.info)]
