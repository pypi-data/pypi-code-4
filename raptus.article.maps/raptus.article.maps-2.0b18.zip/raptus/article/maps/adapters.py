from zope import interface, component

from Products.CMFCore.utils import getToolByName

from raptus.article.maps.interfaces import IMap, IMaps, IMarkers

class Maps(object):
    """ Provider for maps contained in an article
    """
    interface.implements(IMaps)
    
    def __init__(self, context):
        self.context = context
        
    def getMaps(self, **kwargs):
        """ Returns a list of maps (catalog brains)
        """
        if not 'path' in kwargs:
            kwargs['path'] = {'query': '/'.join(self.context.getPhysicalPath()),
                              'depth': 1}
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='Map', sort_on='getObjPositionInParent', **kwargs)

class Markers(object):
    """ Provider for markers contained in a map
    """
    interface.implements(IMarkers)
    component.adapts(IMap)
    
    def __init__(self, context):
        self.context = context
        
    def getMarkers(self):
        """ Returns a list of markers (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='Marker', path={'query': '/'.join(self.context.getPhysicalPath()),
                                                   'depth': 1})
