from plone.stringinterp.adapters import _recursiveGetMembersFromIds
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


def listed_users_with_local_role(content, role, include_global_role=True):
    # union with set of ids of members with the local role
    portal = getSite()
    acl_users = getToolByName(portal, 'acl_users')

    # union with set of ids of members with the local role
    principals = set([p_id for p_id, m_roles
                   in acl_users._getAllLocalRoles(content).items()
                   if role in m_roles])
    if include_global_role:
        portal_role_manager = acl_users.portal_role_manager
        principals |= set([p[0]
                    for p in portal_role_manager.listAssignedPrincipals(role)])

    # get members from group or member ids
    members = _recursiveGetMembersFromIds(portal, principals)
    return [user for user in members if user.getProperty('listed')]


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
