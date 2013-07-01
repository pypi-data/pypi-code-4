from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.nesting.interfaces import IArticles
from raptus.article.core import interfaces, RaptusArticleMessageFactory as _
from raptus.article.teaser.interfaces import ITeaser

REFERENCE = False
try:
    from raptus.article.reference.interfaces import IReference
    REFERENCE = True
except ImportError:
    pass


class ISlideshow(interface.Interface):
    """ Marker interface for the slideshow viewlet
    """


class Component(object):
    """ Component which lists the articles with their images on a timeline
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Slideshow')
    description = _(u'Renders the contained articles in a slideshow.')
    image = '++resource++slideshow.gif'
    interface = ISlideshow
    viewlet = 'swisshaus.article.slideshow'

    def __init__(self, context):
        self.context = context


class Viewlet(ViewletBase):
    """ Viewlet listing the articles in a slideshow
    """
    index = ViewPageTemplateFile('slideshow.pt')
    component = 'slideshow'

    @property
    @memoize
    def articles(self):
        provider = IArticles(self.context)
        manageable = interfaces.IManageable(self.context)
        items = provider.getArticles(component=self.component)
        items = manageable.getList(items, self.component)
        for item in items:
            item.update({'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'url': item['brain'].hasDetail and item['brain'].getURL() or None})
            if item.has_key('show') and item['show']:
                item['class'] = 'hidden'
            if REFERENCE:
                reference = IReference(item['obj'])
                url = reference.getReferenceURL()
                if url:
                    item['url'] = url
            teaser = ITeaser(item['obj'])
            item['image'] = teaser.getTeaserURL()
        return items
