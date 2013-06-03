################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: institutionoverview.py 236195 2011-03-19 15:20:40Z schiele $

from zope.component import getUtility
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
from Products.PythonScripts.standard import url_quote_plus

from ..interfaces import IKeywordExtractor

class InstitutionOverview(BrowserView):

    def getCurrentPath(self):
        return '/'.join(self.context.getPhysicalPath())

    @memoize
    def getData(self):
        """
        Return sorted KeywordList for businessArea
        """
        extractor = getUtility(IKeywordExtractor)
        path = self.getCurrentPath()
        areas = extractor.subjects(self.context, path, query_index='BusinessArea', type='Institution', sort_on='sortable_title')
        for item in areas:
            item['link'] = url_quote_plus(item['BusinessArea'])
            current = []
            for brain in item['brains']:
               current.append(brain)
            if not current:
                del areas[areas.index(item)]
            else:
                current.sort(lambda x, y : cmp(x['Title'].strip().lower(),y['Title'].strip().lower()))
                item['brains'] = current
        return areas

