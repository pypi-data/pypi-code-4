from Acquisition import aq_inner, aq_parent
from zope import interface, component
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interfaces import IATImage
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core.config import MANAGE_PERMISSION
from raptus.article.core import interfaces, RaptusArticleMessageFactory as _
from raptus.article.images.interfaces import IImage

MEDIA = False
try:
    from raptus.article.media.interfaces import IVideoEmbed, IVideo, IVideoEmbedder
    MEDIA = True
except ImportError:
    pass

TEASER = False
try:
    from raptus.article.teaser.interfaces import ITeaser
    TEASER = True
except ImportError:
    pass


class IMediagallery(interface.Interface):
    """ Marker interface for the media gallery viewlet
    """


class Component(object):
    """ Component which lists the media contained in the article
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Media')
    description = _(u'List of the contained media (images and videos) in a horizontal gallery.')
    image = '++resource++mediagallery.gif'
    interface = IMediagallery
    viewlet = 'raptus.article.mediagallery'

    def __init__(self, context):
        self.context = context


class Viewlet(ViewletBase):
    """ Viewlet listing media contained in the article
    """
    index = ViewPageTemplateFile('mediagallery.pt')
    thumb_size = "mediagallery"
    component = "mediagallery"

    def _data(self, item):
        item.update({'title': item['brain'].Title,
                     'description': item['brain'].Description,
                     'class': ''})
        if item.has_key('show') and item['show']:
            item['class'] += ' hidden'
        if IATImage.providedBy(item['obj']):
            img = IImage(item['obj'])
            item['image'] = img.getImage(self.thumb_size)
        elif MEDIA and IVideoEmbed.providedBy(item['obj']):
            embedders = component.getAdapters((item['obj'],), IVideoEmbedder)
            item['embed'] = True
            item['url'] = item['brain'].getRemoteUrl
            for name, embedder in embedders:
                if embedder.matches():
                    item['code'] = embedder.getEmbedCode()
                    item['provider'] = embedder.name
        elif MEDIA and IVideo.providedBy(item['obj']):
            view = component.queryMultiAdapter((item['obj'], self.request,), name='flowplayer')
            teaser = ITeaser(item['obj'])
            item['image'] = teaser.getTeaser(self.thumb_size)
            item['embed'] = False
            item['url'] = view is None and item['brain'].getURL() or view.href()

    @memoize
    def media(self):
        manageable = interfaces.IManageable(self.context)
        mship = getToolByName(self.context, 'portal_membership')
        catalog = getToolByName(self.context, 'portal_catalog')
        args = {}
        if not interfaces.IArticleEditView.providedBy(self.view) or not mship.checkPermission(MANAGE_PERMISSION, self.context):
            args['component'] = self.component
        types = [IATImage.__identifier__]
        if TEASER:
            types.append(interfaces.IArticle.__identifier__)
        if MEDIA:
            types.extend([IVideo.__identifier__,
                          IVideoEmbed.__identifier__])
        items = catalog(object_provides=types,
                        path={'query': '/'.join(self.context.getPhysicalPath()),
                              'depth': 1},
                        sort_on='getObjPositionInParent',
                        **args)
        items = manageable.getList(items, self.component)
        groups = []
        main = None
        for item in items:
            if interfaces.IArticle.providedBy(item['obj']):
                item.update({'title': item['brain'].Title,
                             'description': item['brain'].Description,
                             'childs': []})
                teaser = ITeaser(item['obj'])
                item['image'] = teaser.getTeaser(self.thumb_size + 'group')
                childs = catalog(object_provides=[IATImage.__identifier__,
                                                  IVideo.__identifier__,
                                                  IVideoEmbed.__identifier__],
                                 path={'query': '/'.join(item['obj'].getPhysicalPath()),
                                       'depth': 1},
                                 sort_on='getObjPositionInParent',
                                 **args)
                if not len(childs):
                    continue
                childs = manageable.getList(childs, self.component)
                for child in childs:
                    self._data(child)
                    item['childs'].append(child)
                groups.append(item)
            else:
                self._data(item)
                if main is None:
                    ptypes = getToolByName(self.context, 'portal_types')
                    context = self.context
                    while interfaces.IArticle.providedBy(context) and not context.Schema()['detail'].get(context):
                        context = aq_parent(context)
                    type = ptypes.getTypeInfo(context).Title()
                    main = {'title': _(u'Media of this ${type}', mapping={'type': translate(type, context=self.request)}),
                            'description': None,
                            'childs': []}
                    groups.append(main)
                main['childs'].append(item)
        return groups
