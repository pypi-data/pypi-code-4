from zope import interface
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('raptus.article.maps.interfaces')

security.declarePublic('IMaps')
class IMaps(interface.Interface):
    """ Provider for maps contained in an article
    """
    
    def getMaps(**kwargs):
        """ Returns a list of maps (catalog brains)
        """

security.declarePublic('IMarkers')
class IMarkers(interface.Interface):
    """ Provider for markers contained in a map
    """
    
    def getMarkers(**kwargs):
        """ Returns a list of markers (catalog brains)
        """

class IMap(interface.Interface):
    """ Marker interface for the map content type
    """

class IMarker(interface.Interface):
    """ Marker interface for the marker content type
    """
