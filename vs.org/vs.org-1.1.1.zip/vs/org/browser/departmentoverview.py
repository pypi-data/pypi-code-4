################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: departmentoverview.py 236234 2011-03-21 07:42:05Z ajung $

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.view import memoize
from zope.component import getUtility

from ..interfaces import IKeywordExtractor

class DepartmentOverview(BrowserView):
    """ Default view, all departments """

    def getCurrentPath(self):
        return '/'.join(self.context.getPhysicalPath())

    @memoize
    def getData(self):
        """ return sorted KeywordList for specialisation """

        catalog = getToolByName(self.context, 'portal_catalog')
        wf_tool = getToolByName(self.context, 'portal_workflow')
        extractor = getUtility(IKeywordExtractor)
        path = self.getCurrentPath()
        specs = extractor.subjects(self.context, path, 
                                   query_index='Specialisation', 
                                   type='Department', 
                                   sort_on='sortable_title')

        result = []
        for spec in specs:
            current = {'Specialisation': spec['Specialisation'], 'deps':[]}
            
            for brain in spec['brains']:
                obj = brain.getObject()
                institution = obj.getInstitution()
                # include department only if parent institution is published
                if wf_tool.getInfoFor(institution, 'review_state') in ('published',):
                    current['deps'].append({'department': brain , 'institution': institution})

            if current['deps']:
                current['deps'].sort(lambda x, y : cmp(x['institution']['Title'].strip().lower(),y['institution']['Title'].strip().lower()))
                result.append(current)

        return result

