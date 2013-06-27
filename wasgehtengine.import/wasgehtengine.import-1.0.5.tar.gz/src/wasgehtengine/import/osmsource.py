from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from wasgehtengine.contenttypes.osmelement import OsmElement
from wasgehtengine.contenttypes.geoposition import GeoPosition

import logging
import urllib
import urlparse
from lxml import etree

class OsmSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.normalizer = queryUtility(IIDNormalizer)

        self.type = 'wasgehtengine.Venue'
        self.logger = logging.getLogger(name)
        self.basepath = 'venues/'
        
    def process_tags(self, item, elem):
        for tag in elem.xpath('tag'):
            
            # If node has a name, use it for path instead of ID
            if tag.get('k') == 'name':
                item['_path'] = self.basepath + self.normalizer.normalize(tag.get('v'))
                item['title'] = tag.get('v')
                
            elif tag.get('k') == 'contact:website' or tag.get('k') == 'website':
                # need to convert internationalized domain names to pure ascii hostnames
                website = tag.get('v').encode('idna')
                
                url = urlparse.urlparse(website)
                        
                if not url.scheme:
                    url = urlparse.urlparse('http://' + website)
                            
                item['website'] = url.geturl()
            elif tag.get('k').startswith('addr:'):
                item['postalAddress'][tag.get('k')[5:]] = tag.get('v')
            elif tag.get('k') == 'contact:phone':
                item['phoneNumber'] = tag.get('v')             
            else:
                item['osmReference'].osmElementTags[tag.get('k')] = tag.get('v')
                
    def area_size(p):
        return 0.5 * abs(sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(p)))
    
    def segments(p):
        return zip(p, p[1:] + [p[0]])
                
    def calculate_area_centroid(self, item, tree, elem):
        
        way_id = elem.get('id')
        nodes = tree.xpath("/osm/node[@id = /osm/way[@id = '" + way_id + "']/nd/@ref]")

        lat = sum([float(node.xpath('@lat')[0]) for node in nodes]) / len(nodes) 
        lon = sum([float(node.xpath('@lon')[0]) for node in nodes]) / len(nodes)
        
        return GeoPosition({'latitude': lat, 'longitude': lon})
        

    def __iter__(self):
        for item in self.previous:

            f = urllib.urlopen('http://www.overpass-api.de/api/xapi?' + item['query_params'])
            
            tree = etree.parse(f)
            
            for elem in tree.xpath("/osm/*[tag/@k = 'name']"):
                item = {}
                item['_type'] = self.type
                item['creators'] = ['osm-venue-importer']
                item['osm-id'] = elem.get('id')
                item['transitions'] = ["publish"]
                item['postalAddress'] = {}
                
                osmElementType = 'Node' if elem.tag == 'node' else 'Way'
                item['osmReference'] = OsmElement({'osmElementId': item['osm-id'], 'osmElementType': osmElementType, 'osmElementTags': {}})
                
                if elem.get('lat'):
                    item['geographicPosition'] = GeoPosition({'latitude': elem.get('lat'), 'longitude': elem.get('lon')})
                else:
                    item['geographicPosition'] = self.calculate_area_centroid(item, tree, elem)
                
                self.process_tags(item, elem)
                self.logger.info('Importing venue "'+ item['title'] + '"')
                
                yield item
                item = None