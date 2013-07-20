from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
from lxml import etree
import os

class OsmImportDefinitionSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.logger = logging.getLogger(name)

        self.file = options.get('file','')

    def __iter__(self):
        for item in self.previous:
            yield item
            
        with open(self.file) as definition_file:
            tree = etree.parse(definition_file)
                        
            queries = tree.getroot().findall('query')
            
            for query in queries:
                
                for type in query.get('elements').split(','):
                    
                    query_params = type
                    
                    for predicate in query.findall('predicate'):
                        query_params += ('[' + predicate.text + ']')
                    
                    item = { 'query_params': query_params }
                    print(query_params)
                                           
                    yield item