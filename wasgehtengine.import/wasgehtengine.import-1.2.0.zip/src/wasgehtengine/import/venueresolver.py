from zope.interface import classProvides, implements
from zope import component
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.relation import create_relation
from urlparse import urlparse

import logging

class VenueResolverSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        
        self.catalog = getToolByName(self.context, 'portal_catalog')

        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            
            
            if 'identify_venue_by' in item and item['identify_venue_by'] == 'name' and 'venue_name' in item:
                self.logger.debug('Searching venue with Title "' + item['venue_name'] + '"...')
                results = self.catalog.searchResults({'portal_type': 'wasgehtengine.Venue', 'Title': item['venue_name']})
                
                for brain in results:
                    if brain.getObject().title == item['venue_name']:
                        item['venue'] = create_relation(brain.getPath())
                
                if not 'venue' in item:
                    self.logger.warning('Did not find a venue with title "' + item['venue_name'] + '" in database. Dropping the events.')
                    continue
            
            else:
                url = urlparse(item['venue_website'])
                
                self.logger.debug('Searching venue with website "' + url.netloc + '"...')
            
                results = self.catalog.searchResults({'portal_type': 'wasgehtengine.Venue', 'website': url.netloc})
            
                if len(results) == 0:
                    self.logger.warning('Did not find a venue with website ' + url.netloc + ' in database. Dropping the events.')
                    continue
                
                elif len(results) == 1:
                    item['venue'] = create_relation(results[0].getPath())
                
                elif len(results) > 1 and not 'identify_venue_by' in item:
                    self.logger.warning('Found more than one venue with website ' + item['venue_website'] + ' in database:')
                    for brain in results:
                        self.logger.warning(brain.getPath())
                    
                    self.logger.warning('Using the first one.')
                        
                    item['venue'] = create_relation(results[0].getPath())
                
                elif 'identify_venue_by' in item and item['identify_venue_by'] == 'fullurl':
                        
                    for brain in results:
                        if brain.getObject().website == url.geturl():
                            item['venue'] = create_relation(brain.getPath())
                            
                    if not 'venue' in item:
                        self.logger.warning('Did not find a venue with fullurl ' + url.geturl() + ' in database. Dropping the events.')
                        continue
            
            yield item