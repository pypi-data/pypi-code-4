from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.membrane.interfaces import IMembraneUserFactoryPlugin
from Products.membrane.plugins.userfactory import MembraneUserFactory

from fourdigits.remotemembrane.interfaces import IRemoteMembraneUserFactory


class RemoteMembraneUserFactory(MembraneUserFactory):

    security = ClassSecurityInfo()

    implements(IMembraneUserFactoryPlugin, IRemoteMembraneUserFactory)

    def __init__(self, id, portal_id):
        self.id = id
        self.title = id
        self.portal_id = portal_id

    security.declarePrivate('createUser')

    def createUser(self, user_id, name):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_user_factory.createUser(user_id,
                                                                   name)
        return result
