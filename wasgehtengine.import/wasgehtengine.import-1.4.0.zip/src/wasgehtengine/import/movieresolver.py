from zope.interface import classProvides, implements
from zope import component
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.relation import create_relation
from urlparse import urlparse

import logging

class MovieResolverSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        
        self.catalog = getToolByName(self.context, 'portal_catalog')

        self.logger = logging.getLogger(name)

    def __iter__(self):
        for item in self.previous:
            
            if 'movie_title' in item:
            
                results = self.catalog.searchResults({'portal_type': 'wasgehtengine.Movie', 'Title': item['movie_title']})
                
                for brain in results:
                    if brain.getObject().title == item['movie_title']:
                        item['movie'] = create_relation(brain.getPath())
                
                if not 'movie' in item:
                    self.logger.warning('Did not find a movie with title "' + item['movie_title'] + '" in database. Dropping the screenings.')
                    continue
            
            yield item