from Products.CMFCore.utils import getToolByName
from plone.app.contentmenu.interfaces import IActionsSubMenuItem

from zope import interface
from zope.browsermenu.menu import BrowserSubMenuItem
from zope.component import getMultiAdapter

from p4a.subtyper import subtyperMessageFactory as _

class SubtypesSubMenuItem(BrowserSubMenuItem):
    interface.implements(IActionsSubMenuItem)

    title = _(u'Sub-types')
    description = u''
    submenuId = u'subtypes'
    order = 9
    extra = {'id': 'subtypes'}

    @property
    def action(self):
        return self.context.absolute_url()+ '/subtypes'

    def available(self):
        """decide wether or not to show the subtyper-menu"""

        # don't show the menu if the item doesn't have any subtypes
        view = getMultiAdapter((self.context, self.request), name=u'subtyper')
        if not view.has_possible_types():
            return False

        # We'll show the menu only to managers,
        # see also the permission in p4a.subtyper's configure.zcml
        # TODO: p4a should set it own permissions
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission('Manage portal', self.context):
            return True
        else:
            return False
