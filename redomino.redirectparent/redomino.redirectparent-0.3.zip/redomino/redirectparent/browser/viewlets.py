# -*- coding: utf-8 -*-
from zope.interface import implements, alsoProvides
from zope.viewlet.interfaces import IViewlet
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from redomino.redirectparent.interface import IRedirectToParent
from plone.app.layout.navigation.interfaces import INavigationRoot 
from Acquisition import aq_parent, aq_inner
from plone.app.layout.navigation.defaultpage import isDefaultPage
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

class Redirect(ViewletBase):
    """ redirect to parent if a user can't modify
    """

    def index(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)
        container = aq_parent(context)

        if isDefaultPage(container, context):
            context = container


        # avoid redirecting if we are visiting an url different from the url of the context
        viewname = self.context.getLayout()
        if self.request.URL != self.context.absolute_url() and self.request.URL != self.context.absolute_url() + '/' + viewname:
            return ''

        originalcontext = context

        while all([not INavigationRoot.providedBy(context),
                   IRedirectToParent.providedBy(context), 
                   not sm.checkPermission(ModifyPortalContent, context)]):
#            contextid = context.id
            context = aq_parent(context)

        if context != originalcontext:
            viewurl = getMultiAdapter((context, self.request), name='plone_context_state').view_url()
            self.request.RESPONSE.redirect(viewurl + '#content=' + originalcontext.absolute_url())

        return ''


class GoBack(ViewletBase):
    """ link to parent if a user can modify
    """

    def index(self):
        context = aq_inner(self.context)

        container = aq_parent(context)

        if isDefaultPage(container, context):
            context = container

        originalcontext = context

        # avoid redirecting if we are visiting an url different from the url of the context
        viewname = self.context.getLayout()
        if self.request.URL != self.context.absolute_url() and self.request.URL != self.context.absolute_url() + '/' + viewname:
            return ''

        while all([not INavigationRoot.providedBy(context),
                   IRedirectToParent.providedBy(context)]):
#            contextid = context.id
            context = aq_parent(context)

        if context != originalcontext:
            viewurl = getMultiAdapter((context, self.request), name='plone_context_state').view_url()
            return u'<a class="redirect-to-parent" href="%s">%s</a>' % (viewurl + '#content=' + originalcontext.absolute_url(),context.Title())
        else:
            return ''

TEMPLATE = """\
<script>
(function (w){

w.REDIRECT_TO_PARENT = {
    obj_path:'%(path)s',
    obj_uid:'%(uid)s'
};

}(window));
</script>
"""

class GoBackToRelateScript(ViewletBase):

    def index(self):
        context = self.context
        path = '/'.join(context.getPhysicalPath())

        try:
            uid = context.UID()
        except:
            uid = ''

        return TEMPLATE % locals()

class GoBackToRelate(ViewletBase):
    """ link to related content
    """


    def index(self):
        url = self.request.form.get('relatesToURL')
        path = self.request.form.get('relatesToPath')
        uid = self.request.form.get('relatesToUID')
        
        out = []

        if url:
            out.append(u'<a class="redirect-to-parent" href="%s">&nbsp;</a>' % url)
        if path:
            catalog = getMultiAdapter((self.context, self.request), name='plone_tools').catalog()
            try:
                brain = catalog.searchResults(path={'query':path, depth:0})[0]
                out.append( u'<a class="redirect-to-parent" href="%s">%s</a>' % (brain.getURL(), brain.Title)                            )
            except IndexError:
                out.append('')
        if uid:
            if uid != "None":
                rc = getToolByName(self.context, 'reference_catalog')
                ctx = rc.lookupObject(uid)
                viewurl = getMultiAdapter((ctx, self.request), name='plone_context_state').view_url()
            else:
                ctx = getMultiAdapter((self.context, self.request), name='plone_portal_state').portal()
            out.append( u'<a class="redirect-to-parent" href="%s">%s</a>' % (ctx.absolute_url(), ctx.Title())                            )

        return ''.join(out)
