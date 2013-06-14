from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.membrane.interfaces import IMembraneUserManagerPlugin
from Products.membrane.plugins.usermanager import MembraneUserManager
from fourdigits.remotemembrane.interfaces import IRemoteMembraneUserManager


class RemoteMembraneUserManager(MembraneUserManager):
    """ PAS plugin for managing contentish members in Plone.
    """
    meta_type = 'Remote Membrane User Manager'

    security = ClassSecurityInfo()

    implements(IMembraneUserManagerPlugin, IRemoteMembraneUserManager)

    def __init__(self, id, portal_id):
        self.id = id
        self.title = id
        self.portal_id = portal_id

    # IAuthenticationPlugin implementation
    security.declarePrivate('authenticateCredentials')

    def authenticateCredentials(self, credentials):
        """ See IAuthenticationPlugin.

        o We expect the credentials to be those returned by
          ILoginPasswordExtractionPlugin.
        """
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.authenticateCredentials(
                                                                credentials)
        return result

    # IUserEnumerationPlugin implementation
    security.declarePrivate('enumerateUsers')

    def enumerateUsers(self,
                       id=None,
                       login=None,
                       exact_match=False,
                       sort_by=None,
                       max_results=None,
                       **kw):
        """ See IUserEnumerationPlugin.
        """
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.enumerateUsers(id,
                                                                login,
                                                                exact_match,
                                                                sort_by,
                                                                max_results,
                                                                **kw)
        return result

    # IUserIntrospection implementation
    security.declarePrivate('getUserIds')

    def getUserIds(self):
        """Return a list of user ids"""
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.getUserIds()
        return result

    security.declarePrivate('getUserNames')

    def getUserNames(self):
        """Return a list of usernames"""
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.getUserNames()
        return result

    security.declarePrivate('getUsers')

    def getUsers(self):
        """Return a list of users"""
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.getUserNames()
        return result

    def _getUserChanger(self, login):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users._getUserChanger(login)
        return result

    # IUserManagement implementation
    # (including IMembraneUserChanger implementation)

    def doChangeUser(self, login, password, **kwargs):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.doChangeUser(login,
                                                              password,
                                                              **kwargs)
        return result

    def doDeleteUser(self, login):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.doDeleteUser(login)
        return result

    def doAddUser(self, login, password):
        """
        This is highly usecase dependent, so it delegates to a local
        utility
        """
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.doAddUser(login, password)
        return result

    def allowDeletePrincipal(self, login):
        """
        Check to see if the user can be deleted by trying to adapt
        to an IMembraneUserDeleter
        """
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_users.allowDeletePrincipal(login)
        return result
