# -*- coding: utf-8 -*-
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
import sys

from importlib import import_module
facebook = import_module('wasgehtengine.import.event_import_definitions.facebook')

class PyTransformSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        
        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
                        
            if 'https://www.facebook.com' in item['page_url']:
                self.parser = facebook.FacebookEventParser
            elif not 'script' in item:
                yield item
                continue
            else:
                # TODO: Is there a better way to do this?
                sys.path.insert(0, item['eventimport_definition_directory'])
                self.parser = getattr(__import__(item['script']), 'Parser')
            
            for parsed_item in self.parser(item, item['page']):                    
                yield parsed_item