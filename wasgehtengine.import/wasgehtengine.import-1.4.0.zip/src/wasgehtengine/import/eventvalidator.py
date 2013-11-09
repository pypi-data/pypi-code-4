from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility
from wasgehtengine.contenttypes.behaviors import generate_id

import logging

class EventValidatorSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.normalizer = queryUtility(IIDNormalizer)

        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            if 'ignore' in item and item['ignore'] == True:
                yield item
                continue
            
            if not 'title' in item or item['title'] is None or item['title'] == '':
                self.logger.warning('Event has no title, dropping it.')
                continue
            
            if not 'start' in item or item['start'] is None:
                self.logger.warning('Event with title "'+item['title'] + '" has no startdate, dropping it.')
                continue
            
            if not 'venue' in item or item['venue'] is None:
                self.logger.warning('Event with title "'+item['title'] + '" has no venue, dropping it.')
                continue
            
            venue_path = item['venue'].to_path            
            
            if not '_type' in item:
                item['_type'] = 'wasgehtengine.Screening' if 'movie_title' in item else 'wasgehtengine.Event'
                
            if item['_type'] == 'wasgehtengine.Screening' and item['movie_title']  == '':
                self.logger.warning('Screening movie has no title, dropping it.')
                continue
            
            if not '_path' in item:
                id = self.normalizer.normalize(generate_id(item['title'], item['start'], item['venue']))
                item['_path'] = ('screenings/' if 'movie_title' in item else 'events/') + id
                
            item['creators'] = ['event-importer']
            item['transitions'] = ["publish"]
            
            if not 'website' in item:
                item['website'] = item['page_url']
            
            # If events do not have a precise start time, set it to 20:00
            # so that they are not listed on the previous evening/night at 00:00
            
            if item.get('no_starttime', False) == True:
                item['start'] = item['start'].replace(hour = 20, minute=0)
                        
            if item['_type'] == 'wasgehtengine.Event':
                self.logger.info(venue_path + ': Importing event "' + item['title'] + '"')
            elif item['_type'] == 'wasgehtengine.Screening':
                self.logger.info(venue_path + ': Importing screening of movie "' + item['movie_title'] + '"')
            
            yield item