from Acquisition import aq_base
from Products.CMFDynamicViewFTI import interfaces as interfaces_dynamic_view
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from p4a.subtyper import interfaces
from p4a.subtyper import subtyperMessageFactory as _
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implements


class ISubtyperView(Interface):

    def possible_types():
        pass

    def has_possible_types():
        pass

    def change_type():
        pass


class SubtyperView(BrowserView):
    """View for introspecting and possibly changing subtype info for the
    current context.
    """
    implements(ISubtyperView)

    def possible_types(self):
        subtyper = getUtility(interfaces.ISubtyper)
        return subtyper.possible_types(self.context)

    def has_possible_types(self):
        types = [subtype for subtype in self.possible_types()]
        return len(types) > 0

    def _redirect(self, msg):
        url = self.context.absolute_url()
        if hasattr(aq_base(self.context), 'getLayout'):
            layout = self.context.getLayout() or ''
            if layout:
                if not url.endswith('/'):
                    url += '/'
                url += layout
        IStatusMessage(self.request).addStatusMessage(msg, type='info')
        self.request.response.redirect(url)
        return ''

    def change_type(self):
        """Change the sub type of the current context.
        """

        subtyper = getUtility(interfaces.ISubtyper)

        subtype_name = self.request.get('subtype', None)
        if subtype_name:
            existing = subtyper.existing_type(self.context)
            subtype = subtyper.get_named_type(subtype_name)
            if existing is not None and existing.name == subtype_name:
                selected_layout = False
                dynamic_view = interfaces_dynamic_view.IDynamicallyViewable(
                        self.context, None)
                if dynamic_view is not None:
                    if self.context.getLayout() in\
                            dynamic_view.getAvailableViewMethods():
                        selected_layout = True
                subtyper.remove_type(self.context)
                msg = _(u'Removed ${title} subtype',
                        mapping={'title': subtype.title})
                # Check if the default view has disappeared:
                if selected_layout:
                    dynamic_view =\
                        interfaces_dynamic_view.IDynamicallyViewable(
                            self.context, None)
                    if dynamic_view is None or (self.context.getLayout() in
                       dynamic_view.getAvailableViewMethods()):
                        if self.context.hasProperty('layout'):
                            self.context.manage_delProperties(['layout'])
            else:
                subtyper.change_type(self.context, subtype_name)
                msg = _(u'Changed subtype to ${title}',
                        mapping={'title': subtype.title})
        else:
            msg = _(u'No subtype specified')

        return self._redirect(msg)
