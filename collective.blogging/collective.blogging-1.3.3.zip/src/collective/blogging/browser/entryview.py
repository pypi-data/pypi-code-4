from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_inner

from Products.ATContentTypes.interface import (IATNewsItem, IATEvent, IATLink, IATImage,
                                                IATFile)

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

from plone.app.discussion.interfaces import IConversation
from plone.memoize import view
from collective.blogging.interfaces import IBloggingView


class EntryView(BrowserView):
    """ An entry browser view """

    implements(IBloggingView)

    template = ViewPageTemplateFile('entryview.pt')

    def __call__(self):
        # Link related
        if self.is_link and not self.embed_code:
            if self.redirect_links() and not self.can_edit():
                return self.context.REQUEST.RESPONSE.redirect(self.context.getRemoteUrl())
        
        return self.template()
    
    def getFieldValue(self, name, obj=None):
        if obj is None:
            obj = self.context

        field = obj.getField(name)
        if field:
            return field.get(obj)
        return None
    
    # News Item related
    @property
    def is_newsitem(self):
        return IATNewsItem.providedBy(self.context)

    # File related
    @property
    def is_file(self):
        return IATFile.providedBy(self.context)
    
    # Image related
    @property
    def is_image(self):
        return IATImage.providedBy(self.context)
    
    # Event related
    @property
    def is_event(self):
        return IATEvent.providedBy(self.context)

    # Link related
    @property
    def is_link(self):
        return IATLink.providedBy(self.context)

    @property
    def embed_code(self):
        if self.is_link:
            context = aq_inner(self.context)
            return context.getField('embedCode').get(context)
        return None

    @view.memoize
    def redirect_links(self):
        ptool = getToolByName(self.context, 'portal_properties')
        return getattr(ptool.site_properties, 'redirect_links', False)
    
    @view.memoize
    def can_edit(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('Modify portal content', self.context)

    @property
    def commetns_allowed(self):
        context = aq_inner(self.context)
        return getMultiAdapter((context, self.request), name=u'conversation_view').enabled()

    @property
    def reply_count(self):
        context = aq_inner(self.context)
        discussion = IConversation(context)
        return discussion.total_comments
