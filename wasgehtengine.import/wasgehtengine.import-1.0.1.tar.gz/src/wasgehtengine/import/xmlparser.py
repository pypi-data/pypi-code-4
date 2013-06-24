from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
import requests
import urllib2
from lxml import etree

class XmlParserSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context

        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            if item['format'] == 'xml' and not 'page' in item:
                res = requests.get(item['page_url'])
                    
                # works because the 38 character encoding declaration is sliced off
                # would otherwise throw 'Unicode strings with encoding declaration are not supported.'
                # TODO fix properly
                item['page'] = etree.fromstring(res.text[38:])
                #item['page_string'] = res.content 
                            
            yield item