from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer

import logging
from lxml import etree

class XslTransformSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context

        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            
            if not 'stylesheet' in item:
                yield item
                continue
            
            try:
                stylesheet = etree.parse(item['stylesheet'], base_url=item['stylesheet_baseurl'])
            
                transform = etree.XSLT(stylesheet)
            except etree.XSLTParseError as e:
                print e
                continue
            except etree.XMLSyntaxError as e:
                print e
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
                item['eventlist'] = transform(item['page'])
            
            yield item