################################################################
# vs.flexigridsearch (C) 2011, Veit Schiele GmbH
# Written by Andreas Jung (ZOPYX Ltd)
################################################################

import time
import demjson
from logging import getLogger
from Missing import Missing
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

LOG = getLogger('vs.flexigridsearch')

def _c(s):
    """ Convert string to unicode """
    if isinstance(s, Missing):
        return u''
    if isinstance(s, str):
        return unicode(s or '', 'utf-8')
    return s

class Search(BrowserView):
    """ AJAX/JSON view flexigrid performing the catalog search """

    def __call__(self):

        LOG.info('Query: %r' % self.request.form)
        ts = time.time()

        pprops = getToolByName(self.context, 'portal_properties')
        search_props = getToolByName(pprops, 'flexigridsearch_properties')
        columns = [col.strip() for col in search_props.columns if col.strip()]

        sort_limit = search_props.sort_limit
        max_hits_from_catalog = search_props.max_hits_from_catalog
        portal_types = search_props.portalTypesToSearch
        batch_size = int(self.request['rp'])
        batch_number= int(self.request['page']) - 1
        sort_on = self.request['sortname']
        sort_order = self.request['sortorder'] == 'asc' and 'ascending' or 'descending'
        text = self.request.get('SearchableText')

        language = self.request.LANGUAGE[:2]
        ts_service = getToolByName(self.context, 'translation_service')
        catalog = getToolByName(self.context, 'portal_catalog')
        toLocalTime = self.context.toLocalizedTime

        result = [b for b in catalog(portal_type=portal_types,
                                     SearchableText=text,
                                     sort_limit=sort_limit, 
                                     sort_on=sort_on, 
                                     sort_order=sort_order)]
        len_result = len(result)
        batched_result = result[batch_size*batch_number : (batch_number+1)*batch_size]

        rows = list()
        for brain in batched_result:
            cells = list()
            for column in columns:
                try:
                    value = getattr(brain, column)
                except AttributeError:
                    value = 'n/a'
    
                if column == 'Title':
                    cells.append(u'<a href="%s">%s</a>' % (brain.getURL(),_c(brain.Title)))
                elif column in ('created', 'start', 'end', 'effective', 'expires', 'modified'):
                    try:
                        cells.append(_c(toLocalTime(value)))
                    except:
                        cells.append('')
                elif column in ('Subject',):
                    cells.append(_c(u', '.join([s for s in value if s])))
                else:
                    if column in ('portal_type', 'review_state'):
                        value = ts_service.translate(value, 
                                                     domain='plone', 
                                                     target_language=language, 
                                                     context=self.context)
                    cells.append(_c(value))
            rows.append(dict(id=brain.getId, cell=cells))

        LOG.info('%2.3f seconds' % (time.time() - ts))
        return demjson.encode(dict(page=batch_number+1, 
                                   total=len_result, 
                                   rows=rows))
