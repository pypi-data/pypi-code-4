################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

"""
Define a browser view for the Employee content type. In the FTI
configured in profiles/default/types/Employee.xml, this is being set as the default
view of that content type.
"""

from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize

class EmployeeView(BrowserView):
    """Default view of an employee """

    __call__ = ViewPageTemplateFile('employee_view.pt')
