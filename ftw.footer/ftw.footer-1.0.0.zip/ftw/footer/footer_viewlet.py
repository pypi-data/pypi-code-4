from AccessControl import getSecurityManager
from ftw.footer.interfaces import IFooterSettings
from plone.app.layout.viewlets import common
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility


GRIDROWS = 16  # This should be configurable thru registry


class FooterViewlet(common.ViewletBase):

        index = ViewPageTemplateFile('footer_viewlet.pt')

        def calculate_width(self):
            columns = self.get_column_count()
            width = GRIDROWS / columns
            return width

        def calculate_index(self, manager):
            self.managers = self.get_managers()
            index = self.managers[manager]['index']
            return (index - 1) * self.calculate_width()

        def get_managers(self):
            managers = {}
            for counter in range(1, 5):
                manager = getUtility(IPortletManager,
                                     name='ftw.footer.column%s' % str(
                                        counter))
                mapping = getMultiAdapter((self.context, manager),
                              IPortletAssignmentMapping).__of__(self.context)
                managers['ftw.footer.column%s' % str(counter)] = {
                        'empty': not bool(mapping.keys()), 'index': counter}
            return managers

        def generate_classes(self, manager):
            width = self.calculate_width()
            index = self.calculate_index(manager)
            classes = 'column cell position-%s width-%s' % (index, width)
            return classes

        def is_column_visible(self, index):
            columns = self.get_column_count()
            return bool(index <= columns)

        def has_permission(self):
            sm = getSecurityManager()
            return bool(sm.checkPermission('ftw.footer: Manage Footer',
                                           self.context))

        def get_column_count(self):
            registry = getUtility(IRegistry)
            footer_settings = registry.forInterface(IFooterSettings,
                check=False)
            if not footer_settings:
                return 0
            count = footer_settings.columns_count
            return count
