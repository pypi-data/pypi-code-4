# Test package.

from dolmen.authentication import IPrincipal
from zope.interface import implements

class User(object):
    implements(IPrincipal)
  
    def __init__(self, id, title=u"", desc=u""):
        self.id = id
        self.title = title or id
        self.description = desc
        self.groups = []
