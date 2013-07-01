from zope.interface import alsoProvides, noLongerProvides
from zope.component import queryAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from raptus.article.core import interfaces


class ShowHideItem(BrowserView):
    """Shows/hides an item in a component
    """

    def __call__(self, action, uid, component, anchor=''):
        self.redirect(anchor)
        if not queryAdapter(self.context, interface=interfaces.IComponent, name=component):
            return '0'
        item = self.get_item(uid)
        if not item:
            return '0'
        try:
            components = list(item.Schema()['components'].get(item))
        except:
            return '0'
        if action == 'show' and not component in components:
            item.Schema()['components'].set(item, components+[component,])
            item.reindexObject()
        if action == 'hide' and component in components:
            item.Schema()['components'].set(item, [c for c in components if not c == component])
            item.reindexObject()
        return '1'

    def get_item(self, uid):
        catalog = getToolByName(self.context, 'uid_catalog')
        results = catalog(UID=uid)
        if not len(results):
            return None
        return results[0].getObject()

    def redirect(self, anchor):
        if self.request.get('ajax_load', 0):
            return
        self.request.RESPONSE.redirect('%s/@@edit.components#%s' % (self.context.absolute_url(), anchor))
