from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

try: # Plone 4 and higher
    from Products.ATContentTypes.interfaces.image import IATImage
except: # BBB Plone 3
    from Products.ATContentTypes.interface.image import IATImage

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.images.interfaces import IImages, IImage

class ILightbox(interface.Interface):
    """ Marker interface for the lightbox viewlet
    """

class Component(object):
    """ Component which shows a lightbox of the images
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Lightbox')
    description = _(u'Lightbox of the images contained in the article.')
    image = '++resource++lightbox.gif'
    interface = ILightbox
    viewlet = 'raptus.article.lightbox'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the lightbox of the images
    """
    index = ViewPageTemplateFile('lightbox.pt')
    css_class = "componentFull"
    img_size = "lightbox"
    component = "lightbox"
    
    @property
    @memoize
    def images(self):
        items = []
        provider = IImages(self.context)
        images = provider.getImages(component=self.component)
        for image in images:
            obj = image.getObject()
            img = IImage(obj)
            item = {'caption': img.getCaption(),
                    'img': img.getImageURL(self.img_size),}
            items.append(item)
        return items

class ILightboxTeaser(interface.Interface):
    """ Marker interface for the lightbox teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a lightbox of the images displayed above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Lightbox teaser')
    description = _(u'Lightbox of the images contained in the article displayed above the columns.')
    image = '++resource++lightbox_teaser.gif'
    interface = ILightboxTeaser
    viewlet = 'raptus.article.lightbox.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(Viewlet):
    """ Viewlet showing the lightbox of the images displayed above the columns
    """
    css_class = "componentFull"
    img_size = "lightboxteaser"
    component = "lightbox.teaser"
