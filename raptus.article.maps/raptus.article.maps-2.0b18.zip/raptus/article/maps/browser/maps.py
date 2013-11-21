from Acquisition import aq_inner
from zope import interface, component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.maps.interfaces import IMaps, IMarkers

class IMapsLeft(interface.Interface):
    """ Marker interface for the maps left viewlet
    """

class ComponentLeft(object):
    """ Component which lists the maps on the left side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Maps left')
    description = _(u'List of maps contained in the article on the left side.')
    image = '++resource++maps_left.gif'
    interface = IMapsLeft
    viewlet = 'raptus.article.maps.left'
    
    def __init__(self, context):
        self.context = context

class ViewletLeft(ViewletBase):
    """ Viewlet listing the maps on the left side
    """
    index = ViewPageTemplateFile('maps.pt')
    css_class = "componentLeft maps-left"
    component = "maps.left"
    
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
    def maps(self):
        provider = IMaps(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getMaps(component=self.component), self.component)
        i = 0
        l = len(items)
        for item in items:
            item.update({'uid': item['brain'].UID,
                         'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'class': self._class(item['brain'], i, l),
                         'markers': []})
            manageable_map = interfaces.IManageable(item['obj'])
            item['markers'] = manageable_map.getList(IMarkers(item['obj']).getMarkers())
            for marker in item['markers']:
                marker.update({'uid': marker['brain'].UID,
                               'title': marker['brain'].Title,
                               'description': marker['brain'].Description,
                               'text': marker['obj'].getText()})
            i += 1
        return items

class IMapsRight(interface.Interface):
    """ Marker interface for the maps right viewlet
    """

class ComponentRight(object):
    """ Component which lists the maps on the right side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Maps right')
    description = _(u'List of maps contained in the article on the right side.')
    image = '++resource++maps_right.gif'
    interface = IMapsRight
    viewlet = 'raptus.article.maps.right'
    
    def __init__(self, context):
        self.context = context

class ViewletRight(ViewletLeft):
    """ Viewlet listing the maps on the right side
    """
    css_class = "componentRight maps-right"
    component = "maps.right"

class IMapsFull(interface.Interface):
    """ Marker interface for the maps full viewlet
    """

class ComponentFull(object):
    """ Component which lists the maps over the whole width
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Maps')
    description = _(u'List of maps contained in the article over the whole width.')
    image = '++resource++maps_full.gif'
    interface = IMapsFull
    viewlet = 'raptus.article.maps.full'
    
    def __init__(self, context):
        self.context = context

class ViewletFull(ViewletLeft):
    """ Viewlet listing the maps over the whole width
    """
    css_class = "componentFull maps-full"
    component = "maps.full"
    
