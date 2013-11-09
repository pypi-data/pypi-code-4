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
    
    def build_url(self, base_url, parameters, datetime):
        if parameters == None or len(parameters) == 0:
            return base_url
        
        return base_url + ('&' if '?' in base_url else '?') + self.generate_parameters(parameters, datetime)

    def __iter__(self):
        for item in self.previous:
            
            if 'ignore' in item and item['ignore'] == True:
                yield item
                continue
                   
            scope = item.get('scope', 'month')     
            look_ahead_days = 1 if scope == 'all' else item.get('look-ahead-days', 31)
            
            if scope == 'month':
                interval = 30
            else:
                interval = 1
                               
            for days in xrange(0, look_ahead_days, interval):
                new_item = item.copy()
                day = self.now + timedelta(days)
                new_item['page_url'] = self.build_url(item['base_url'], item.get('parameters', None), day)
                new_item['start'] = day
                yield new_item