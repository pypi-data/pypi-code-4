from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility
from datetime import datetime

import logging

class OsmImportStatusLogger(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.logger = logging.getLogger(name)
        self.normalizer = queryUtility(IIDNormalizer)
        self.counts = {};


    def __iter__(self):
        for item in self.previous:
            
            if not 'query_params' in item:
                self.logger.info(str(item))
            
            normalized_query = self.normalizer.normalize(item['query_params'])
            
            if not normalized_query in self.counts:
                self.counts[normalized_query] = 0
            
            if item.get('ignore', False) == True:
                
                item['_path'] = '/osmimportstatus/' + normalized_query
                
                now = datetime.now()
                
                item['creators'] = ['osm-venue-importer']
                item['transitions'] = ["publish"]
                item['title'] = 'OpenStreetMap venue import status for query ' + item['query_params']
                item['last_run'] = now
                item['last_successful_run'] = now
                
                if self.counts[normalized_query] > 0:
                    item['last_run_with_venues_imported'] = now
                    
                item['imported_venues_count'] = self.counts[normalized_query]
                
                yield item
                continue
            
            self.counts[normalized_query] += 1
            yield item