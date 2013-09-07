from types import NoneType

from OFS.ObjectManager import ObjectManager
from webdav.NullResource import NullResource


if hasattr(ObjectManager, 'get'):
    ObjectManager.__old__get = ObjectManager.get

    def get(self, key, default=None):
        if key in self.objectIds():
            return self.__old__get(key, default)
        return default

    ObjectManager.get = get


def __getitem__(self, key):
    if key in self.objectIds():
        return self._getOb(key, None)
    request = getattr(self, 'REQUEST', None)
    if not isinstance(request, (str, NoneType)):
        method=request.get('REQUEST_METHOD', 'GET')
        if (request.maybe_webdav_client and
            method not in ('GET', 'POST')):
            return NullResource(self, key, request).__of__(self)
    raise KeyError, key


ObjectManager.__getitem__ = __getitem__
