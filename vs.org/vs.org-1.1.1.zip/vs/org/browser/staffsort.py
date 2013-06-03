################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from plone.memoize.instance import memoize

from zope.interface import implements
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from Products.Five.browser import BrowserView

from .interfaces import IStaffSortView
from ..content import employeefolder

class StaffSortView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getSortedStaff(self):
        """ Return sorted Userlist """

        result = []
        users = list(self.context.getEmployees())
        for user in users:
            c_dic = {
                'degree':       user.getDegree(),
                'degree_after':       user.getDegreeAfter(),
                'firstname':    user.getFirstname(),
                'lastname':     user.getLastname(),
                'position':     user.getPosition(),
                'url':         user.absolute_url(),
                'DisplayNamePosition':  user.DisplayNamePosition(),
            }
            result.append(c_dic)
        return result

    # The 'available' property is used to determine if the portlet should
    # be shown.

    @property
    def available(self):
        return len(self._data()) > 0

    # To make the view template as simple as possible, we return dicts with
    # only the necessary information.

    def employeefolder(self):
        for brain in self._data():
            employee = brain.getObject()
            yield dict(title=registrant.name,
                       url=brain.getURL())

    # By using the @memoize decorator, the return value of the function will
    # be cached. Thus, calling it again does not result in another query.
    # See the plone.memoize package for more.

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        limit = self.data.count

        query = dict(object_provides = IEmployee.__identifier__)

        query['sort_on'] = 'modified'
        query['sort_order'] = 'reverse'
        query['sort_limit'] = limit
        if not self.data.sitewide:
            query['path'] = '/'.join(context.getPhysicalPath())

        # Ensure that we only get active objects, even if the user would
        # normally have the rights to view inactive objects (as an
        # administrator would)
        query['effectiveRange'] = DateTime()

        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(query)
        employeefolder = results[:limit]

        return employeefolder
