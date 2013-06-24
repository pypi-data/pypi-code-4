from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.media.interfaces import IVideos as IVideoProvider, ITeaser, IVideoEmbed, IVideoEmbedder

class IVideos(interface.Interface):
    """ Marker interface for the videos viewlet
    """

class Component(object):
    """ Component which lists the video files
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Videos')
    description = _(u'List of the video files contained in the article.')
    image = '++resource++video.gif'
    interface = IVideos
    viewlet = 'raptus.article.media.video'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet listing the video files
    """
    index = ViewPageTemplateFile('video.pt')
    
    def _class(self, brain, i, l):
        cls = []
        if i == 0:
            cls.append('first')
        if i == l-1:
            cls.append('last')
        if i % 2 == 0:
            cls.append('odd')
        if i % 2 == 1:
            cls.append('even')
        return ' '.join(cls)

    @property
    @memoize
    def show_title(self):
        """hide or show title. this can be set with a property in portal_porperties. 
        """
        props = getToolByName(self.context, 'portal_properties').raptus_article
        return props.getProperty('media_video_title', True)

    @property
    @memoize
    def videos(self):
        provider = IVideoProvider(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getVideos())
        i = 0
        l = len(items)
        for item in items:
            view = component.queryMultiAdapter((item['obj'], self.request,), name='flowplayer')
            item.update({'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'class': self._class(item['brain'], i, l),
                         'url': view is None and item['brain'].getURL() or view.href(),
                         'embed': False})
            if IVideoEmbed.providedBy(item['obj']):
                embedders = component.getAdapters((item['obj'],), IVideoEmbedder)
                item['embed'] = True
                item['url'] = item['brain'].getRemoteUrl
                for name, embedder in embedders:
                    if embedder.matches():
                        item['code'] = embedder.getEmbedCode()
                        item['provider'] = embedder.name
            else:
                img = ITeaser(item['obj'])
                item['img'] = img.getTeaser()
            i += 1
        return items
