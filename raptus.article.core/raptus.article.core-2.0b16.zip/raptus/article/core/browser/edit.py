from zope import interface, component

from plone.app.layout.viewlets.common import ViewletBase
from plone.app.viewletmanager import manager

from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.article.core import interfaces, componentfilter


class View(BrowserView):
    """ Edit view of an article
    """
    interface.implements(interfaces.IArticleEditView)
    template = ViewPageTemplateFile('view.pt')

    def __call__(self):
        self.request.set('raptus_article_viewing', False)
        return self.template()


class Toggle(ViewletBase):
    """ View/Edit toggle
    """
    index = ViewPageTemplateFile('toggle.pt')

    def update(self):
        self.editing = interfaces.IArticleEditView.providedBy(self.view)
        if self.editing:
            self.save = '%s/@@save.components' % self.context.absolute_url()
            self.cancel = self.context.absolute_url()
        else:
            self.edit = '%s/@@edit.components' % self.context.absolute_url()


class Move(BrowserView):
    """ Helper view to move objects in articles
    """

    def __call__(self, item, target):
        if not item in self.context or not target in self.context:
            return '0'
        delta = self.context.getObjectPosition(target) - self.context.getObjectPosition(item)
        if not delta:
            return '0'
        self.context.moveObjectsByDelta([item], delta)
        return delta


class ViewletManager(BrowserView):
    """ Renders a specific viewlet manager with the given components activated
    """

    def __call__(self, manager, components=None, actual=False):
        if components is None:
            components = []
        if isinstance(components, basestring):
            components = [components]
        view = component.getMultiAdapter((self.context, self.request), name='edit.components')
        manager = component.getMultiAdapter((self.context, self.request, view), name=manager)
        if not actual:
            comps = interfaces.IComponents(self.context)
            provided = []
            not_provided = []
            for name, comp in comps.getComponents():
                if comp.interface.providedBy(self.context):
                    if not name in components:
                        provided.append(comp.interface)
                        interface.noLongerProvides(self.context, comp.interface)
                elif name in components:
                    not_provided.append(comp.interface)
                    interface.alsoProvides(self.context, comp.interface)
        manager.update()
        result = manager.render()
        if not actual:
            for iface in not_provided:
                interface.noLongerProvides(self.context, iface)
            for iface in provided:
                interface.alsoProvides(self.context, iface)
        return result


class OrderedViewletManager(manager.OrderedViewletManager):
    """ Viewlet manager with custom rendering used in raptus articles edit view
    """
    template = ViewPageTemplateFile('manager.pt')

    def render(self):
        self.view = getattr(self, '__parent__', None)
        self.name = self.__name__
        self.url = '%s/@@components?manager=%s' % (self.context.absolute_url(), self.__name__)
        components = interfaces.IComponents(self.context).getComponents()
        sorter = component.getMultiAdapter((self.context, self.request, self.view), interfaces.IComponentFilter)
        components = sorter.filter(components, self.__name__)
        self.components = len(components)
        return super(OrderedViewletManager, self).render()
