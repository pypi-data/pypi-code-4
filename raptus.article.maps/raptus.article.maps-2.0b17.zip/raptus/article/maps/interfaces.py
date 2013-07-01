from zope import interface

class IMaps(interface.Interface):
    """ Provider for maps contained in an article
    """
    
    def getMaps(**kwargs):
        """ Returns a list of maps (catalog brains)
        """

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
