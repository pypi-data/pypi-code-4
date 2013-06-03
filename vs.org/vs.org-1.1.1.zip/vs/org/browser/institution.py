################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class InstitutionView(BrowserView):
    """Default view, one institution """

    __call__ = ViewPageTemplateFile('institution_view.pt')

