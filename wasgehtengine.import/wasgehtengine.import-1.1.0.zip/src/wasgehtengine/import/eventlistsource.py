from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from datetime import datetime
import logging
from lxml import etree

def parse_datetime(date_element, time_element):
        if date_element is None:
            return None
        
        if time_element is None:
            return datetime.strptime(date_element.text, '%Y-%m-%d')
        
        return datetime.strptime(date_element.text + 'T' + time_element.text, '%Y-%m-%dT%H:%M:%S')

class EventListSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context

        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            
            if not 'eventlist' in item:
                yield item
                continue
            
            tree = item['eventlist']
            
            for event in tree.xpath('//event'):
                item = item.copy()
                
                #item['date'] = event.xpath('occurrence[1]/start-date')
                
                item['title'] = event.find('name').text.strip()
                item['description'] = event.find('description').text.strip()

                item['start_datetime'] = parse_datetime(event.find('occurrence/start-date'), event.find('occurrence/start-time'))
                item['end_datetime'] = parse_datetime(event.find('occurrence/end-date'), event.find('occurrence/end-time'))
                                                    
                yield item