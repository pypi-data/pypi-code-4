from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging

class ReturnStatusSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            
            if item.get('ignore', False) == True:
                if len(item['all_errors']) != 0:
                    raise Exception(item['all_errors'])
            
            yield item
