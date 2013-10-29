from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
from lxml.html import html5parser, tostring
import chardet
import urllib2
import traceback

class HtmlParserSection(object):
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
                item['htmlparser_errors'] = self.errors
                yield item
                continue
            
            if item['format'] == 'html' and not 'page' in item:
                content = urllib2.urlopen(item['page_url']).read()
                
                encoding = False
                
                if 'force_encoding' in item:
                    encoding = item['force_encoding']
                    self.logger.debug('forced encoding '+encoding)
                elif 'guess_encoding' in item:
                    encoding = chardet.detect(content)['encoding']
                    self.logger.debug('detected encoding ' + encoding)
                    
                if encoding and encoding != 'utf-8':
                    self.logger.debug('not unicode, converting...')
                    content = content.decode(encoding, 'replace').encode('utf-8')
                
                try:
                    item['page'] = html5parser.fromstring(content)
                except Exception as e:
                    self.errors.append(traceback.format_exc())
                    self.logger.warning('Exception occured while parsing.')
                
                #item['page_string'] = tostring(item['page']) 
                            
            yield item