from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
import requests
import urllib2
from lxml import etree
import traceback

class XmlParserSection(object):
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
                item['xmlparser_errors'] = self.errors
                yield item
                continue
            
            if item['format'] == 'xml' and not 'page' in item:
                res = requests.get(item['page_url'])
                    
                # works because the 38 character encoding declaration is sliced off
                # would otherwise throw 'Unicode strings with encoding declaration are not supported.'
                # TODO fix properly
                try:
                    item['page'] = etree.fromstring(res.text[38:])
                except Exception as e:
                
                    self.errors.append(traceback.format_exc())
                    self.logger.warning('Exception occured while parsing.')
                #item['page_string'] = res.content 
                            
            yield item