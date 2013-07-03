from zope import interface

class IVideos(interface.Interface):
    """ Provider for video files and embedded ones contained in an article
    """
    
    def getVideos(**kwargs):
        """ Returns a list of video files and embedded ones (catalog brains)
        """

class ITeaser(interface.Interface):
    """ Handler for image thumbing of videos
    """
        
    def getTeaserURL(size="original"):
        """
        Returns the url to the teaser image in the specific size
        
        The sizes are taken from the raptus_article properties sheet
        and are formed by the following name schema:
        
            media_<size>_(height|width)
        """
    
    def getTeaser(size="orginal"):
        """ 
        Returns the html tag of the teaser image in the specific size
        
        The sizes are taken from the raptus_article properties sheet
        and are formed by the following name schema:
        
            media_<size>_(height|width)
        """
        
    def getSize(size):
        """
        Returns the width and height registered for the specific size
        """

class IVideo(interface.Interface):
    """ Marker interface for the video content type
    """
        
class IVideoEmbed(interface.Interface):
    """ Marker interface for the video embed content type
    """
    
class IVideoEmbedder(interface.Interface):
    """ Provides html for different video providers
    """
    
    name = interface.Attribute('name', 'User friendly name of this embeder')
    
    def matches():
        """Whether the embeder matches the adapted obj or not
        """
    
    def getEmbedCode():
        """ Returns the html
        """

class IAudios(interface.Interface):
    """ Provider for audio files contained in an article
    """
    
    def getAudios(**kwargs):
        """ Returns a list of audio files (catalog brains)
        """

class IAudio(interface.Interface):
    """ Marker interface for the audio content type
    """
