from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
import os

class CrawlPagesExpanderSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            
            for crawl_page in item['crawl_pages']:
                crawl_page_item = item.copy()
                            
                if crawl_page.get('stylesheet'):
                    crawl_page_item['stylesheet'] = os.path.join(item['eventimport_definition_directory'], crawl_page.get('stylesheet'))
                                
                if crawl_page.get('script'):
                    crawl_page_item['script'] = crawl_page.get('script')
                    
                if crawl_page.get('eventlinks-script'):
                    crawl_page_item['eventlinks-script'] = crawl_page.get('eventlinks-script')
                                
                if crawl_page.get('eventlinks-stylesheet'):
                    crawl_page_item['eventlinks_stylesheet'] = os.path.join(item['eventimport_definition_directory'], crawl_page.get('eventlinks-stylesheet'))
                    
                if crawl_page.get('force-encoding'):
                    crawl_page_item['force_encoding'] = crawl_page.get('force-encoding')
                    
                if crawl_page.get('guess-encoding'):
                    crawl_page_item['guess_encoding'] = crawl_page.get('guess-encoding')
                                
                crawl_page_item['base_url'] = crawl_page.get('url')
                crawl_page_item['format'] =  crawl_page.get('format')
                            
                crawl_page_item['parameters'] = {}
                
                for parameter in crawl_page.xpath('date-parameter'):
                    crawl_page_item['parameters'][parameter.get('name')] = parameter.get('pattern')
                            
                yield crawl_page_item
