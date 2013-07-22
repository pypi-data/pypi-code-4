from Acquisition import aq_inner

from zope import interface, component
from zope.event import notify

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces, event


class Components(BrowserView):
    """Component selection
    """

    template = ViewPageTemplateFile('components.pt')

    def __call__(self, manager=None):
        self.manager = manager
        self.action = '%s/@@components' % self.context.absolute_url()
        if manager is not None:
            self.action += '?manager=%s' % manager
        if self.request.get('form.submitted', False) or self.request.get('form.view', False):
            statusmessage = IStatusMessage(self.request)
            if self._save():
                statusmessage.addStatusMessage(_(u'Components saved successfully'), u'info')
            else:
                statusmessage.addStatusMessage(_(u'Saving components failed'), u'error')
            if self.request.get('ajax_load', 0):
                return '1'
        if self.request.get('form.view', False):
            return self.context.absolute_url() or self.request.RESPONSE.redirect(self.context.absolute_url())
        return self.template()

    def _save(self):
        try:
            context = aq_inner(self.context)
            components = interfaces.IComponents(context).getComponents()
            sorter = component.getMultiAdapter((context, self.request, self), interfaces.IComponentFilter)
            components = sorter.filter(components, self.manager)
            active = self.request.form.get('form.components', ())
            for name, comp in components:
                if name in active:
                    if comp.interface.providedBy(context):
                        continue
                    interface.alsoProvides(context, comp.interface)
                    notify(event.ComponentActivatedEvent(context, comp.interface))
                elif comp.interface.providedBy(context):
                    interface.noLongerProvides(context, comp.interface)
                    notify(event.ComponentDeactivatedEvent(context, comp.interface))
        except:
            return False
        return True

    @property
    @memoize
    def components(self):
        context = aq_inner(self.context)
        components = interfaces.IComponents(context).getComponents()
        sorter = component.getMultiAdapter((context, self.request, self), interfaces.IComponentFilter)
        components = sorter.filter(components, self.manager)
        items = []
        for name, comp in components:
            items.append({'name' : name,
                          'title' : comp.title,
                          'description' : comp.description,
                          'image' : comp.image,
                          'selected' : comp.interface.providedBy(context)})
        return items
