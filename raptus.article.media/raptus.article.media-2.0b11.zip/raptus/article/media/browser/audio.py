from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.media.interfaces import IAudios as IAudioProvider

class IAudios(interface.Interface):
    """ Marker interface for the audios viewlet
    """

class Component(object):
    """ Component which lists the audio files
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Audio')
    description = _(u'List of the audio files contained in the article.')
    image = '++resource++audio.gif'
    interface = IAudios
    viewlet = 'raptus.article.media.audio'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet listing the audio files
    """
    index = ViewPageTemplateFile('audio.pt')
    
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
    def audios(self):
        provider = IAudioProvider(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getAudios())
        i = 0
        l = len(items)
        for item in items:
            view = component.getMultiAdapter((item['obj'], self.request,), name='flowplayer')
            item.update({'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'class': self._class(item['brain'], i, l),
                         'url': view.href()})
            i += 1
        return items
