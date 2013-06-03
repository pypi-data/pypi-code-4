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

class IEqualInstitutionsPortlet(IPortletDataProvider):
    """
    """
    institution_uid = schema.TextLine(
        title    = _(u'label_uid'),
        required = True,
    ) 
    
class EqualInstitutionsPortletAssignment(base.Assignment):
    implements(IEqualInstitutionsPortlet)
    institution_uid = '' 

    def __init__(self, institution_uid=''):
        self.institution_uid = institution_uid
    
    @property
    def title(self):
        return _(u'label_equalinstitutionsportlet')

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('equalinstitutionsportlet.pt')

    # @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        data = self.getOtherInstitutions()
        for item in data:
            if item['institutions'] :    
                return True
        return False
    
    def getOtherInstitutions(self):
        inst_data = self.getInstitutionData()
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        items = []
        for area in inst_data['areas']:
            items.append({'area': area, 'institutions': []})
            institutions = catalog(BusinessArea=area, Type='Institution')
            for inst in institutions:
                if inst.UID != self.data.institution_uid:
                    inst_dic = {
                        'title':        inst.Title,    
                        'url':          inst.getURL(), 
                        'description':  inst.Description 
                    }
                    items[-1]['institutions'].append(inst_dic)
        return items
            

    def getInstitutionData(self):
        inst_data = {'areas': [], 'path': ''}
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        uid = self.data.institution_uid
        if uid:
             result = list(catalog(UID=uid,))
             if len(result):
                inst_data['areas'] = list(result[0].BusinessArea)
                inst_data['path'] = result[0].getPath()
        return inst_data 
 
class AddForm(base.NullAddForm):
    form_fields = form.Fields(IEqualInstitutionsPortlet)

    def create(self):
        return EqualInstitutionsPortletAssignment(institution_uid=self.context.UID())


