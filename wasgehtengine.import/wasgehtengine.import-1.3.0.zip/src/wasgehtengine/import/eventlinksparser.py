from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
import sys
import traceback

from importlib import import_module
facebook = import_module('wasgehtengine.import.event_import_definitions.facebook')

class EventlinksParserSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context

        self.logger = logging.getLogger(name)
        self.errors = []

    def __iter__(self):
        for item in self.previous:
            
            if 'ignore' in item and item['ignore'] == True:
                item['eventlinksparser_errors'] = self.errors
                yield item
                continue
            
            if 'https://www.facebook.com' in item['page_url']:
                self.parser = facebook.FacebookEventlinksParser
            elif not 'eventlinks-script' in item:
                yield item
                continue
            else:
                # TODO: Is there a better way to do this?
                sys.path.insert(0, item['eventimport_definition_directory'])
                self.parser = getattr(__import__(item['eventlinks-script']), 'Parser')
            
            page = item['page']
            del item['page']
            
            try:
                for parsed_item in self.parser(item, page):      
                    yield parsed_item
            except Exception as e:
                self.errors.append(traceback.format_exc())
                self.logger.warning('Exception occured while parsing.')
           