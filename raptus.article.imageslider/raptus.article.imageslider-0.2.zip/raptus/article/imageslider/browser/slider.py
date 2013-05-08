from zope.interface.declarations import implements
from raptus.article.core.interfaces import IComponent, IComponentSelection,\
    IArticle, IManageable
from raptus.article.core.config import MANAGE_PERMISSION
from zope.component import adapts
from zope.interface.interface import Interface
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from raptus.article.images.interfaces import IImages, IImage
from zope.component import getMultiAdapter
from Products.CMFPlone.utils import getToolByName
try: # Plone 4 and higher
    from Products.ATContentTypes.interfaces.image import IATImage
except: # BBB Plone 3
    from Products.ATContentTypes.interface.image import IATImage

from raptus.article.core import RaptusArticleMessageFactory as _

class ISlider(Interface):
    """A marker interface for sliding images viewlet
    """


class ComponentTeaser(object):
    """ Component which displays content images in a carousel
    """
    implements(IComponent, IComponentSelection)
    adapts(IArticle)

    title = _(u'Imageslider (Teaser)')
    description = _(u"Display an image slider above the content which uses"
                     "content aware images as source.")
    image = '++resource++slider-teaser.gif'
    interface = ISlider
    viewlet = 'raputs.article.imageslider.teaser'

    def __init__(self, context):
        self.context = context



class ViewletTeaser(ViewletBase):
    """ Viewlet showing the image fader over the whole width
    """
    index = ViewPageTemplateFile('slider.pt')
    component = 'imageslider.teaser'
    css_class = 'sliderTeaser'

    def update(self):
        super(ViewletTeaser, self).update()
        props = getToolByName(self.context, 'portal_properties').raptus_article
        self.showCaption = props.getProperty('imageslider_teaser_caption', False)
        self.showNav = props.getProperty('imageslider_teaser_navigation', False)
        self.haltTime = props.getProperty('imageslider_teaser_halttime', 6000)
        self.fadeTime = props.getProperty('imageslider_teaser_fadetime', 1500)
        self.width = props.getProperty('images_imagesliderteaser_width', 500)
        self.height = props.getProperty('imageslider_teaser_height', 200)
        self.linkRelatedItems = props.getProperty('imageslider_teaser_link_related', False)
        self.images = self._images()
        


    def _images(self):
        items = []
        mship = getToolByName(self.context, 'portal_membership')
        canManage = mship.checkPermission(MANAGE_PERMISSION, self.context)
        if canManage:
            images = IImages(self.context).getImages()
        else:
            images = IImages(self.context).getImages(component=self.component)


        manageable = IManageable(self.context)
        images = manageable.getList(images, self.component)

        for item in images:
            img = IImage(item['obj'])
            obj = item['obj']
            
            
            item.update({
                'class': '',
                'caption': obj.Title(),
                'description': obj.Description(),
                'img_url': img.getImageURL('imagesliderteaser'),
                'image_object': obj,
                'link':  obj.getRelatedItems() and obj.getRelatedItems()[0].absolute_url() or None,
            })

            if 'show' in item and item['show']:
                item['class'] += ' hidden'

            items.append(item)

        return items
