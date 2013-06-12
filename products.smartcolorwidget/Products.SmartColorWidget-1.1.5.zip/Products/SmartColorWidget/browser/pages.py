# -*- coding: utf-8 -*-
# $Id: pages.py 9248 2009-11-11 09:51:09Z glenfant $
"""Various Z3 style view/pages for SmartColorWidget"""

from Acquisition import aq_inner
from App.special_dtml import DTMLFile
from Products.Five.browser import BrowserView


class WidgetStylesheet(BrowserView):

    template = DTMLFile('smartcolor_helper.css', globals())

    def __call__(self, *args, **kwargs):
        """Renders my stylesheet.
        Note that:
        * we do not change HTTP headers since we are supposed to be published
        through the CSS registry that takes care of this.
        * according to ZCML, self.context is the Plone site
        """
        context = aq_inner(self.context)
        self.request.RESPONSE.setHeader('Content-Type',
                                        'text/css;charset=utf-8')
        base_properties = getattr(context, 'base_properties')
        resources_url = (context.absolute_url() +
                         '/++resource++smartcolorwidget-static')
        template = self.template.__of__(self.context)
        return template(context=self.context, base_properties=base_properties,
                        resources_url=resources_url)


class MacrosPage(BrowserView):
    """May seem somehow strange but in that case the macros
    are the view itself
    """

    @property
    def macros(self):
        """AT widget asks for the .macros attribute rather than testing
        if the template is a mapping of macros
        """
        return self
