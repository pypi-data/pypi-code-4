from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.PluggableAuthService.interfaces.plugins \
    import IPropertiesPlugin

from Products.PlonePAS.interfaces.plugins import IMutablePropertiesPlugin

from Products.membrane.plugins.propertymanager import MembranePropertyManager
from fourdigits.remotemembrane.interfaces import IRemoteMembranePropertyManager


class RemoteMembranePropertyManager(MembranePropertyManager):
    """ PAS plugin for managing properties on contentish users and groups
        in Plone.
    """

    security = ClassSecurityInfo()

    implements(IPropertiesPlugin,
               IMutablePropertiesPlugin,
               IRemoteMembranePropertyManager)

    def __init__(self, id, portal_id):
        self.id = id
        self.title = id
        self.portal_id = portal_id

    def _getPropertyProviders(self, user):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_roles._getPropertyProviders(user)
        return result

    # IMutablePropertiesPlugin implementation
    # IPropertiesPlugin implementation
    security.declarePrivate('getPropertiesForUser')

    def getPropertiesForUser(self, user, request=None):
        """
        Retrieve all the IMembraneUserProperties property providers
        and delegate to them.
        """
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_properties.getPropertiesForUser(
                                                                    user,
                                                                    request)
        return result

    security.declarePrivate('setPropertiesForUser')

    def setPropertiesForUser(self, user, propertysheet):
        """
        Retrieve all of the IMembraneUserProperties property providers
        and delegate to them.
        """
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_properties.setPropertiesForUser(
                                                            user,
                                                            propertysheet)
        return result
