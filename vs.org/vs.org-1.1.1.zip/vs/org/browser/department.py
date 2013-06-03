################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

"""
Define a browser view for the Department content type. In the FTI
configured in profiles/default/types/Department.xml, this is being set as the default
view of that content type.
"""

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class DepartmentView(BrowserView):
    """ Default view, one department """

    __call__ = ViewPageTemplateFile('department_view.pt')

