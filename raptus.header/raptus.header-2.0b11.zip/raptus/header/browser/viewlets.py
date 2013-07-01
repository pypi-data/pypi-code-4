from zope import component
from zope.interface import implements
from random import *

from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import ViewletBase

from Products.ATContentTypes.interface.image import IATImage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from raptus.header import headerMessageFactory as _
from raptus.header.interfaces import IHeader

from zope.annotation import IAnnotations

from Acquisition import aq_inner, aq_parent

ANNOTATIONS_KEY_DISABLED = 'raptus.header.disabled'
ANNOTATIONS_KEY_ENABLED = 'raptus.header.enabled'

class HeaderViewlet(ViewletBase):
    index = ViewPageTemplateFile('header.pt')
    _info = ViewPageTemplateFile('info.pt')
    
    hasImage = False
    src = ''
    description = ''
    title = ''
    manage = None
    disabled = None
    enabled = None
    info = None

    def __init__(self, context, request, view, manager=None):
        super(HeaderViewlet, self).__init__(context, request, view, manager)
        self.mship = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.props = getToolByName(self.context, 'portal_properties').site_properties
        if self.request.get('enable_header', False) or self.request.get('disable_header', False) or self.request.get('inherit_header', False):
            if not self.mship.checkPermission(permissions.ModifyPortalContent, self.context):
                return
            annotations = IAnnotations(context)
            if self.request.get('enable_header', False):
                if annotations.has_key(ANNOTATIONS_KEY_DISABLED):
                    del annotations[ANNOTATIONS_KEY_DISABLED]
                annotations[ANNOTATIONS_KEY_ENABLED] = True
            elif self.request.get('disable_header', False):
                if annotations.has_key(ANNOTATIONS_KEY_ENABLED):
                    del annotations[ANNOTATIONS_KEY_ENABLED]
                annotations[ANNOTATIONS_KEY_DISABLED] = True
            elif self.request.get('inherit_header', False):
                if annotations.has_key(ANNOTATIONS_KEY_DISABLED):
                    del annotations[ANNOTATIONS_KEY_DISABLED]
                if annotations.has_key(ANNOTATIONS_KEY_ENABLED):
                    del annotations[ANNOTATIONS_KEY_ENABLED]

    @memoize
    def info(self):
        header = self.header()
        if not header or (hasattr(self.context, 'isTemporary') and self.context.isTemporary()) or not self.mship.checkPermission(permissions.ModifyPortalContent, self.context):
            return
        annotations = component.queryAdapter(self.context,interface=IAnnotations)
        if annotations is None:
            return
        self.enable = False
        self.disable = False
        self.inherit = annotations.has_key(ANNOTATIONS_KEY_DISABLED) or annotations.has_key(ANNOTATIONS_KEY_ENABLED)
        if self.disabled:
            self.enable = self.mship.checkPermission(permissions.ModifyPortalContent, self.context)
        else:
            self.disable = self.mship.checkPermission(permissions.ModifyPortalContent, self.context)
        return self._info()

    @memoize
    def header(self):
        self.disabled = None
        self.enabled = None

        parent = aq_inner(self.context)
        while True:
            try:
                if not self.enabled and not self.disabled and IAnnotations(parent).get(ANNOTATIONS_KEY_DISABLED, False):
                    self.disabled = parent
                if not self.disabled and not self.enabled and IAnnotations(parent).get(ANNOTATIONS_KEY_ENABLED, False):
                    self.enabled = parent
            except:
                pass
            brain = self.catalog(object_provides=IHeader.__identifier__,
                                 path={'query': '/'.join(parent.getPhysicalPath()),'depth': 1})
            if len(brain) or IPloneSiteRoot.providedBy(parent) or not self.props.getProperty('header_allow_inheritance', True):
                break
            else:
                parent = aq_parent(parent)
        if not len(brain):
            return
        
        """take the first header-element
        """
        return brain[0]
    
    def update(self):
        self.hasImage = False
        self.responsive = self.props.getProperty('header_responsive', False)
        header = self.header()
        if not header:
            return
        images = self.catalog(object_provides=IATImage.__identifier__,
                              path={'query': header.getPath(),'depth': 1})

        if not len(images):
            return

        image = choice(images)

        if self.responsive:
            self.image = image.getURL() + '/image'
            self.thumb = image.getURL() + '/image_thumb'
        else:
            obj = image.getObject()
            scales = component.getMultiAdapter((obj, obj.REQUEST), name='images')
            w = self.props.getProperty('header_width', 0)
            h = self.props.getProperty('header_height', 0)
            scale = scales.scale('image',
                                 width=(w and w or 1000000),
                                 height=(h and h or 1000000))
            if scale is None:
                return

            self.image = scale.tag()

        self.description = image.Description
        self.title = image.Title

        if self.disabled:
            return

        self.hasImage = True

        try: # if article core exist, so this will load the manage box
            from raptus.article.core import interfaces
            if not hasattr(self.context, 'raptus_article_macros'):
                return
            manageable = interfaces.IManageable(self.context)
            self.manage = manageable.getList([image]).pop()
        except ImportError:
            pass
