from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

from datetime import datetime as dt
from datetime import timedelta

import logging
import urllib

class UrlAssemblerSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context

        self.logger = logging.getLogger(name)
        
        self.now = dt.now()
        
    def replace_datetime_pattern(self, pattern, datetime):
        return datetime.strftime(pattern)
        
    def generate_parameters(self, parameters, datetime):
        params = {}
        
        for key, pattern in parameters.items():
            params[key] = self.replace_datetime_pattern(pattern, datetime)           
        
        return urllib.urlencode(params)

    def __iter__(self):
        for item in self.previous:
                        
            if item['parameters']:
                page_urls = [item['base_url'] + ('&' if '?' in item['base_url'] else '?') + self.generate_parameters(item['parameters'], self.now),
                             item['base_url'] + ('&' if '?' in item['base_url'] else '?') + self.generate_parameters(item['parameters'], self.now + timedelta(30))]
            else:
                page_urls = [item['base_url']]
            
            for page_url in page_urls:
                item = item.copy()
                item['page_url'] = page_url
                yield item