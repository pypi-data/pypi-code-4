from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from Products.CMFCore import permissions as core_permissions

from collective.blogging import _

class BloggerRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_can_blog", default=u"Can blog")
    required_permission = core_permissions.ManagePortal
