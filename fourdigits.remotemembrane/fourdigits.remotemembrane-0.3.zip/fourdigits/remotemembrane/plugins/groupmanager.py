from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.membrane.interfaces import IMembraneGroupManagerPlugin

from Products.membrane.plugins.groupmanager import MembraneGroupManager
from fourdigits.remotemembrane.interfaces import IRemoteMembraneUserManager


class RemoteMembraneGroupManager(MembraneGroupManager):
    """
    PAS plugin for managing contentish groups in Plone.
    """

    security = ClassSecurityInfo()

    implements(IMembraneGroupManagerPlugin, IRemoteMembraneUserManager)

    def __init__(self, id, portal_id):
        self.id = id
        self.title = id
        self.portal_id = portal_id

    # IGroupsPlugin implementation
    security.declarePrivate('getGroupsForPrincipal')

    def getGroupsForPrincipal(self, principal, request=None):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_groups.getGroupsForPrincipal(
                                                        principal, request)
        return result

    # IGroupEnumerationPlugin implementation
    security.declarePrivate('enumerateGroups')

    def enumerateGroups(self,
                        id=None,
                        title=None,
                        exact_match=False,
                        sort_by=None,
                        max_results=None,
                        **kw):
        """
        See IGroupEnumerationPlugin.
        Quite similar to enumerateUsers, but searches for groups
        and uses title instead of login
        """
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_groups.enumerateGroups(id,
                                                                   title,
                                                                   exact_match,
                                                                   sort_by,
                                                                   max_results,
                                                                   **kw)
        return result

    # IGroupsPlugin implementation
    def getGroupById(self, group_id, default=None):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_groups.getGroupById(group_id,
                                                               default)
        return result

    def getGroups(self):
        return map(self.getGroupById, self.getGroupIds())

    def getGroupIds(self):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_groups.getGroupIds()
        return result

    def getGroupMembers(self, group_id):
        portal = getattr(self, self.portal_id)
        result = portal.acl_users.membrane_groups.getGroupMembers(group_id)
        return result
