from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility
from wasgehtengine.contenttypes.period import Period

import logging

class EventValidatorSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.normalizer = queryUtility(IIDNormalizer)

        self.logger = logging.getLogger(name)
        self.basepath = 'events/'
        self.type = 'wasgehtengine.Event'

    def __iter__(self):
        for item in self.previous:
            if not 'title' in item or item['title'] is None:
                self.logger.warning('Event has no title, dropping it.')
                continue
            
            if not 'start' in item or item['start'] is None:
                self.logger.warning('Event with title "'+item['title'] + '" has no startdate, dropping it.')
                continue
            
            if not 'venue' in item or item['venue'] is None:
                self.logger.warning('Event with title "'+item['title'] + '" has no venue, dropping it.')
                continue
            
            item['_path'] = self.basepath + self.normalizer.normalize(item['title']) + '-' + self.normalizer.normalize(item['start'].date().isoformat())
            item['_type'] = self.type
            item['creators'] = ['event-importer']
            item['transitions'] = ["publish"]
            
            if not 'website' in item:
                item['website'] = item['page_url']
            
            # If events do not have a precise start time, set it to 20:00
            # so that they are not listed on the previous evening/night at 00:00
            
            if item.get('no_starttime', False) == True:
                item['start'] = item['start'].replace(hour = 20, minute=0)
                        
            self.logger.info(item['venue'].to_path + ': Importing event "' + item['title'] + '"')
            
            yield item