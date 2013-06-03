################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

"""
Employee folder search view 
"""


from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class EmployeefolderView(BrowserView):
    """Default view of an employeefolder """

    __call__ = ViewPageTemplateFile('employeefolder_view.pt')

    def searchEmployees(self):
        """ Search form callback """
        catalog = getToolByName(self.context, 'portal_catalog')
        vs_sheet = getToolByName(getToolByName(self.context, 'portal_properties'), 'vsorg_properties')
        lastname = self.request.get('lastname', '')
        if lastname:
            # if requested: strip of wildcards
            if vs_sheet.employeeFolderExactSearch:
                lastname = lastname.replace('?', '')
                lastname = lastname.replace('.', '')
                lastname = lastname.replace('*', '')
            return catalog(portal_type='Employee',
                           path='/'.join(self.context.getPhysicalPath()),
                           lastname=lastname)   
        else:
            return ()
