from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
from lxml import etree
import os

class EventImportDefinitionSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.logger = logging.getLogger(name)

        self.directory = options.get('directory','')

    def __iter__(self):
        for item in self.previous:
            yield item
            
            
        for root, subFolders, files in os.walk(self.directory):
            
            for filename in files:
                if filename.endswith('.xml'):
                    definition_filepath = os.path.join(root, filename)
                    
                    with open(definition_filepath) as definition_file:
                        tree = etree.parse(definition_file)
                        
                        enabled = tree.xpath('/event-import/@enabled')[0]
                        
                        if enabled != 'true':
                            continue
                        
                        venue_name = tree.getroot().get('venue-name')
                        venue_website = tree.getroot().get('venue-website')
                        identify_venue_by = tree.getroot().get('identify-venue-by')
                        
                        item = {}                 
                        directory = os.path.dirname(definition_filepath)
                        item['eventimport_definition_path'] = definition_filepath
                        item['eventimport_definition_directory'] = directory
                        item['stylesheet_baseurl'] = 'file://' + directory + '/'
                        item['venue_website'] = venue_website
                        item['crawl_pages'] = tree.xpath('//crawl-page')
                        
                        if venue_name:
                            item['venue_name'] = venue_name
                            
                        if identify_venue_by:
                            item['identify_venue_by'] = identify_venue_by
                        
                        yield item