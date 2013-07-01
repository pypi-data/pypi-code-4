from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.nesting.interfaces import IArticles

TEASER = False
try:
    from raptus.article.teaser.interfaces import ITeaser
    TEASER = True
except:
    pass

REFERENCE = False
try:
    from raptus.article.reference.interfaces import IReference
    REFERENCE = True
except:
    pass

WYSIWYG = False
try:
    from raptus.article.additionalwysiwyg.interfaces import IWYSIWYG
    WYSIWYG = True
except:
    pass

class ISlider(interface.Interface):
    """ Marker interface for the slider viewlet
    """

class Component(object):
    """ Component which shows a slider of the articles
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Slider')
    description = _(u'Slider of the articles contained in the article.')
    image = '++resource++slider.gif'
    interface = ISlider
    viewlet = 'raptus.article.slider'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the slider of the articles
    """
    type = 'slider'
    index = ViewPageTemplateFile('slider.pt')
    css_class = "slider-content componentFull"
    thumb_size = "slider"
    component = "slider"
    
    @property
    @memoize
    def props(self):
        return getToolByName(self.context, 'portal_properties').raptus_article
    
    @property
    @memoize
    def title_pre(self):
        return self.props.getProperty('%s_titletop' % self.type, False)
    
    @property
    @memoize
    def show_caption(self):
        return self.props.getProperty('%s_caption' % self.type, False)
    
    @property
    @memoize
    def wysiwyg(self):
        if not WYSIWYG:
            return False
        return self.props.getProperty('%s_wysiwyg' % self.type, False)
    
    @property
    @memoize
    def description(self):
        return self.props.getProperty('%s_description' % self.type, False)
    
    @property
    @memoize
    def image(self):
        if not TEASER:
            return False
        return self.props.getProperty('%s_image' % self.type, False)
    
    @memoize
    def articles(self):
        provider = IArticles(self.context)
        manageable = interfaces.IManageable(self.context)
        items = provider.getArticles(component=self.component)
        items = manageable.getList(items, self.component)
        i = 0
        l = len(items)
        for item in items:
            item.update({'title': item['brain'].Title,
                         'description': self.description and item['brain'].Description or None,
                         'url': item['brain'].hasDetail and item['brain'].getURL() or None,
                         'class': item.has_key('show') and item['show'] and 'hidden' or ''})
            if REFERENCE:
                reference = IReference(item['obj'])
                url = reference.getReferenceURL()
                if url:
                    item['url'] = url
            if self.image:
                teaser = ITeaser(item['obj'])
                image = {'img': teaser.getTeaser(self.thumb_size),
                         'caption': teaser.getCaption(),
                         'url': None,
                         'rel': None}
                if image['img']:
                    w, h = item['obj'].Schema()['image'].getSize(item['obj'])
                    tw, th = teaser.getSize(self.thumb_size)
                    if item['url']:
                        image['url'] = item['url']
                    elif (tw < w and tw > 0) or (th < h and th > 0):
                        image['rel'] = 'lightbox'
                        image['url'] = teaser.getTeaserURL(size="popup")
                    item['image'] = image
            if self.wysiwyg:
                item['text'] = IWYSIWYG(item['obj']).getAdditionalText()
            i += 1
        return items

class ISliderTeaser(interface.Interface):
    """ Marker interface for the slider teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a slider of the articles displayed above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Slider teaser')
    description = _(u'Slider of the articles contained in the article displayed above the columns.')
    image = '++resource++slider_teaser.gif'
    interface = ISliderTeaser
    viewlet = 'raptus.article.slider.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(Viewlet):
    """ Viewlet showing the slider of the images displayed above the columns
    """
    type = 'sliderteaser'
    css_class = "slider-teaser componentFull"
    thumb_size = "sliderteaser"
    component = "slider.teaser"
