from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.membrane.interfaces import IMembraneRoleManagerPlugin
from Products.membrane.plugins.rolemanager import MembraneRoleManager

from fourdigits.remotemembrane.interfaces import IRemoteMembraneUserManager


class RemoteMembraneRoleManager(MembraneRoleManager):
    """ PAS plugin for managing roles with Membrane.
    """

    security = ClassSecurityInfo()

    implements(IMembraneRoleManagerPlugin, IRemoteMembraneUserManager)

    def __init__(self, id, portal_id):
        self.id = id
        self.title = id
        self.portal_id = portal_id

    #  IRolesPlugin implementation
    security.declarePrivate('getRolesForPrincipal')

    def getRolesForPrincipal(self, principal, request=None):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_roles.getRolesForPrincipal(
                                                                principal,
                                                                request)
        return result
