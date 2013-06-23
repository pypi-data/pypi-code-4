##################################################################
#
# (C) Copyright 2006 ObjectRealms, LLC
# All Rights Reserved
#
# Ed Crewe - modified to make cancel checkout based on whether
# the user can delete the object and it is a checkout rather
# than tying to checkin rights.
#
##################################################################

from zope.component import getMultiAdapter

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import CheckoutException

from plone.memoize.view import memoize
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import DeleteObjects

class Cancel(BrowserView):

    template = ViewPageTemplateFile('cancel.pt')
    
    def __call__(self):
        context = aq_inner(self.context)
        
        if self.request.form.has_key('form.button.Cancel'):
            control = getMultiAdapter((context, self.request), name=u"iterate_control")
            if not self.cancel_allowed():
                raise CheckoutException(u"Not a checkout")

            policy = ICheckinCheckoutPolicy(context)
            baseline = policy.cancelCheckout()
            baseline.reindexObject()
            
            IStatusMessage(self.request).addStatusMessage(_(u"Checkout cancelled"), type='info')
            view_url = baseline.restrictedTraverse("@@plone_context_state").view_url()
            self.request.response.redirect(view_url)
        elif self.request.form.has_key('form.button.Keep'):
            view_url = context.restrictedTraverse("@@plone_context_state").view_url()
            self.request.response.redirect(view_url)
        else:
            return self.template()

    @memoize
    def cancel_allowed(self):
        """ Use instead of the iterate.control.cancel_allowed to cater for
            users without checkin rights to be able to cancel their checkouts
            if they can delete the object.
        """
        object = aq_inner(self.context)
        checkPermission = getSecurityManager().checkPermission
        if not checkPermission(DeleteObjects, object):
            return False

        if hasattr(object,'getRefs') and object.getRefs("Working Copy Relation"):
            return True

        return False
