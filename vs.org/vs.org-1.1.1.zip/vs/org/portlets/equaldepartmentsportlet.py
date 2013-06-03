from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from .. import orgMessageFactory as _

class IEqualDepartmentsPortlet(IPortletDataProvider):
    """
    """
    department_uid = schema.TextLine(
        title    = _(u'label_uid'),
        required = True,
    ) 
    
class EqualDepartmentsPortletAssignment(base.Assignment):
    implements(IEqualDepartmentsPortlet)
    department_uid = '' 

    def __init__(self, department_uid=''):
        self.department_uid = department_uid
    
    @property
    def title(self):
        return _(u'label_equaldepartmentsportlet')

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('equaldepartmentsportlet.pt')

    # @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        data = self.getOtherDepartments()
        for item in data:
            if item['departments'] :    
                return True
        return False
    
    
    def getOtherDepartments(self):
        dep_data = self.getDepartmentData()
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        items = []
        for spec in dep_data['specialisations']:
            items.append({'spec': spec, 'departments': []})
            deps = catalog(Specialisation=spec, Type='Department')
            for dep in deps:
                if dep.UID != self.data.department_uid: # ignore ourself
                    institution = dep.getObject().getInstitution()
                    dep_dic = {
                        'institutionTitle': institution.Title(),    
                        'departmentLink': dep.getURL(), 
                        'departmentTitle': dep.Title ,  
                        'departmentDescription': dep.Description   
                    }
                    items[-1]['departments'].append(dep_dic)
        return items
            

    def getDepartmentData(self):
        dep_data = {'specialisations': [], 'path': ''}
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        uid = self.data.department_uid
        if uid:
             result = list(catalog(UID=uid,))
             if len(result):
                dep_data['specialisations'] = list(result[0].Specialisation)
                dep_data['path'] = result[0].getPath()
                
        return dep_data 
 
class AddForm(base.NullAddForm):
    form_fields = form.Fields(IEqualDepartmentsPortlet)

    def create(self):
        return EqualDepartmentsPortletAssignment(department_uid=self.context.UID())


