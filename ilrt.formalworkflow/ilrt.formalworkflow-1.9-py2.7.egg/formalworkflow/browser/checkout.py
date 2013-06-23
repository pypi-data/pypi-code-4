from Acquisition import aq_inner
from Products.CMFPlone.utils import getToolByName
from zope.component import getAdapters
from plone.app.iterate.interfaces import IWCContainerLocator
from plone.app.iterate.browser.checkout import Checkout as BaseCheckout
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Checkout(BaseCheckout):
    """ Override the template and modify available containers if
        global_checkout_location is set in site_properties
    """
    template = ViewPageTemplateFile('checkout.pt')

    def containers(self):
        """Get a list of potential containers
        """
        context = aq_inner(self.context)
        portal_props = getToolByName(context, 'portal_properties')
        site_props = portal_props.get('site_properties')
        if site_props:
            gc_location = site_props.getProperty('global_checkout_locator', '') 
        else:
            gc_location = ''

        location = {}    
        for name, locator in getAdapters((context,), IWCContainerLocator):
            if locator.available:
                location[name] = locator

        if gc_location not in location.keys():
            for name in location.keys():
                yield dict(name=name, locator=location[name])
        else:
            yield dict(name=gc_location, locator=location[gc_location]) 
