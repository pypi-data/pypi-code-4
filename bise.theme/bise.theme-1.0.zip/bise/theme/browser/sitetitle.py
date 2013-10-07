from five import grok
from zope.component import getMultiAdapter
from zope.interface import Interface


class SiteTitle(grok.View):
    """ View for BAPDatabase tool compatibility"""
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('site_title')

    def render(self):
        pps = getMultiAdapter((self.context, self.request),
            name='plone_portal_state'
        )
        return pps.portal_title()