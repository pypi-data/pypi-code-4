from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
from lxml import etree
import traceback

class XslTransformSection(object):
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
                item['xsltransform_errors'] = self.errors
                yield item
                continue
            
            if not 'stylesheet' in item:
                yield item
                continue
            
            try:
                stylesheet = etree.parse(item['stylesheet'], base_url=item['stylesheet_baseurl'])
            
                transform = etree.XSLT(stylesheet)
            except Exception as e:
                self.errors.append(traceback.format_exc())
                self.logger.warning('Exception occured while parsing.')
                continue
            
            if 'eventlinks_stylesheet' in item:
#                eventlinks_stylesheet = etree.parse(item['eventlinks_stylesheet'], base_url=item['stylesheet_baseurl'])
#                try:
#                    eventlinks_transform = etree.XSLT(eventlinks_stylesheet)
#                except etree.XSLTParseError as e:
#                    print e
#                except etree.XMLSyntaxError as e:
#                    print e
#                    
#                result = eventlinks_transform(item['page'])
                pass
            else:
                try:
                    item['eventlist'] = transform(item['page'])
                except Exception as e:
                    self.errors.append(traceback.format_exc())
                    self.logger.warning('Exception occured while parsing.')
            
            yield item