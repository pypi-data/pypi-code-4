# -*- coding: utf-8 -*-

################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from ..interfaces import IKeywordExtractor


class KeywordExtractor(object):

    implements(IKeywordExtractor)

    def subjects(self, context, root_path, query_index='Subject', type=None, sort_on='sortable_title',depth=None):
        context = aq_inner(context)
        catalog = getToolByName(context, 'portal_catalog')
        keywords = catalog.uniqueValuesFor(query_index)
        result = []
        if not root_path:
            root_path='/'
        for keyword in keywords:
            if not type:
                if depth:
                    all = catalog({'path':{'query':root_path, 'depth': depth}, query_index: keyword , 'sort_on':sort_on})
                else:
                    all = catalog({'path':root_path, query_index: keyword ,'sort_on':sort_on})
            else:
                if depth:
                    all = catalog({'path':{'query': root_path, 'depth':depth}, query_index: keyword ,'Type':type, 'sort_on': sort_on})
                else: 
                    all = catalog({'path':root_path, query_index: keyword ,'Type':type, 'sort_on':sort_on})
            if all:
                size = len(list(all))
                current = {query_index: keyword, 'cnt': size, 'brains': all}
                result.append(current)
        return result
