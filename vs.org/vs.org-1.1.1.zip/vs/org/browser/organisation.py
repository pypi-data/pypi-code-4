################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: organisation.py 236202 2011-03-19 17:33:04Z schiele $

from Acquisition import aq_inner
from Acquisition import aq_parent
 
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote_plus

from plone.memoize.instance import memoize
from zope.component import getUtility
from zope.interface import implements

from ..interfaces import IKeywordExtractor
from .interfaces import IOrganisation
from .departmentoverview import DepartmentOverview
from .institutionoverview import InstitutionOverview


class Organisation(BrowserView):
    """Default view, all institutions """

    implements(IOrganisation)

    @memoize
    def getInstitutionOverview(self):
        """
        """
        i_view = InstitutionOverview(self.context.getInstitution(), self.request)
        return i_view.getData()
    
    @memoize
    def getDepartmentOverview(self):
        """
        """
        i_view = DepartmentOverview(self.context, self.request)
        return i_view.getData()

    def getLocationOverview(self):
        """
        """
        extractor = getUtility(IKeywordExtractor)
        path = '/'.join(aq_parent(aq_inner(self.context)).getPhysicalPath())
        locations = extractor.subjects(aq_parent(aq_inner(self.context)), path, query_index='country', type='Institution', sort_on='sortable_title')
       
        ptool = getToolByName(self.context, 'plone_utils')
        folder_path = aq_parent(aq_inner(self.context)).absolute_url()
        for location in locations:
            tmp = {}
            for brain in location['brains']:
                if brain['province'] not in tmp.keys():
                    normalized = ptool.normalizeString(brain['province']) 
                    tmp[brain['province']] = {'province': brain['province'],'link': "%s/%s" %(folder_path, normalized) ,'brains':[]}
                tmp[brain['province']]['brains'].append(brain)
            for key in tmp.keys():
                tmp[key]['brains'].sort(lambda x, y : cmp(x['Title'].strip().lower(),y['Title'].strip().lower()))
            
            del location['brains']        
            
            t_keys = tmp.keys()
            t_keys.sort() 
            location['provinces'] = [tmp[key] for key in t_keys]

        return locations

    def getDataByBusinessArea(self):

        catalog = getToolByName(self.context, 'portal_catalog')
        areas = catalog.uniqueValuesFor('BusinessArea')

        area2inst = dict()
        for area in areas:
            institutions = list()
            for brain in catalog(portal_type='Institution',
                                 BusinessArea=area,
                                 sort_on='sortable_title'):
                institutions.append(brain.getObject())
            area2inst[area] = institutions

        return dict(areas=areas,
                    area2inst=area2inst)

    def getBusinessAreasForCountryRegion(self):

        catalog = getToolByName(self.context, 'portal_catalog')
        areas = catalog.uniqueValuesFor('BusinessArea')
        country_region = self.request.country_region.lower()

        areas_in_region = list()
        for area in areas:
            for brain in catalog(portal_type='Institution', BusinessArea=area):
                inst = brain.getObject()
                inst_ref = ('%s-%s' % (inst.getCountry(), inst.getProvince())).lower()
                if inst_ref == country_region:
                    areas_in_region.append(dict(area=area, id=area))
                    break
          
        return areas_in_region

    def getInstitutionsInLocationForBusinessArea(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        area = self.request.area
        country_region = self.request.country_region.lower()

        result = list()
        for brain in catalog(portal_type='Institution', BusinessArea=area):
            inst = brain.getObject()
            inst_ref = ('%s-%s' % (inst.getCountry(), inst.getProvince())).lower()
            if inst_ref == country_region:
                result.append(inst)

        return result

    def newId(self):
        count = 0
        while True:
            count += 1
            yield 'node-%d' % count

