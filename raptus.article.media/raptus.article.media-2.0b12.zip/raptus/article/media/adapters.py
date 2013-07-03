from zope import interface, component

from Products.CMFCore.utils import getToolByName

from raptus.article.core.interfaces import IArticle
from raptus.article.media.interfaces import IVideos, IAudios, IVideo, ITeaser

class Videos(object):
    """ Provider for video files contained in an article
    """
    interface.implements(IVideos)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getVideos(self, **kwargs):
        """ Returns a list of video files (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type=['Video', 'VideoEmbed',], path={'query': '/'.join(self.context.getPhysicalPath()),
                                                                   'depth': 1}, sort_on='getObjPositionInParent', **kwargs)

class Teaser(object): 
    """ Handler for image thumbing of videos
    """
    interface.implements(ITeaser)
    component.adapts(IVideo)
    
    def __init__(self, context):
        self.context = context
        
    def getTeaserURL(self, size='video'):
        """
        Returns the url to the teaser image in the specific size
        
        The sizes are taken from the raptus_article properties sheet
        and are formed by the following name schema:
        
            media_<size>_(height|width)
        """
        if not self.context.Schema()['image'].get(self.context):
            return None
        
        w, h = self.getSize(size)
        
        url = '%s/image' % self.context.absolute_url()
        if w or h:
            scales = component.getMultiAdapter((self.context, self.context.REQUEST), name='images')
            scale = scales.scale('image', width=(w or 100000), height=(h or 100000))
            if scale is not None:
                url = scale.url
        return url
        
    def getTeaser(self, size='video'):
        """ 
        Returns the html tag of the teaser image in the specific size
        
        The sizes are taken from the raptus_article properties sheet
        and are formed by the following name schema:
        
            media_<size>_(height|width)
        """
        url = self.getTeaserURL(size)
        if not url:
            return None
        
        return '<img src="%s" alt="" />' % url
        
    def getSize(self, size='video'):
        """
        Returns the width and height registered for the specific size
        """
        props = getToolByName(self.context, 'portal_properties').raptus_article
        return props.getProperty('media_%s_width' % size, 0), props.getProperty('media_%s_height' % size, 0)

class Audios(object):
    """ Provider for audio files contained in an article
    """
    interface.implements(IAudios)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getAudios(self, **kwargs):
        """ Returns a list of audio files (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='Audio', path={'query': '/'.join(self.context.getPhysicalPath()),
                                                  'depth': 1}, sort_on='getObjPositionInParent', **kwargs)
