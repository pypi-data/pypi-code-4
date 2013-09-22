### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
from persistent import Persistent

# import Zope3 interfaces
from zope.app.file.interfaces import IImage
from zope.annotation.interfaces import IAnnotations
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.file.interfaces import IImageDisplay
from ztfy.hplskin.interfaces import IBannerImage, ITopBannerImageAddFormMenuTarget, \
                                    ILeftBannerImageAddFormMenuTarget, IBannerManager, \
                                    IBannerManagerContentsView
from ztfy.skin.interfaces.container import IActionsColumn, IContainerTableViewActionsCell
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.table.column import Column
from z3c.template.template import getLayoutTemplate
from zope.app.file.image import Image
from zope.component import adapts, adapter, getAdapter, queryAdapter, queryMultiAdapter, getUtility
from zope.container.contained import Contained
from zope.i18n import translate
from zope.interface import implements, implementer, Interface
from zope.intid.interfaces import IIntIds
from zope.location import locate
from zope.publisher.browser import BrowserPage
from zope.security.proxy import removeSecurityProxy
from zope.traversing import namespace, api as traversing_api
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.base.ordered import OrderedContainer
from ztfy.file.property import ImageProperty
from ztfy.hplskin.menu import HPLSkinMenuItem, HPLSkinDialogMenuItem
from ztfy.skin.container import OrderedContainerBaseView
from ztfy.skin.form import DialogAddForm
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.hplskin import _


class BannerManager(OrderedContainer):
    """Banner manager"""

    implements(IBannerManager)


BANNER_MANAGER_ANNOTATIONS_KEY = 'ztfy.hplskin.banner.%s'

def BannerManagerFactory(context, name):
    """Banner manager factory"""
    annotations = IAnnotations(context)
    banner_key = BANNER_MANAGER_ANNOTATIONS_KEY % name
    manager = annotations.get(banner_key)
    if manager is None:
        manager = annotations[banner_key] = BannerManager()
        locate(manager, context, '++banner++%s' % name)
    return manager


class BannerManagerNamespaceTraverser(namespace.view):
    """++banner++ namespace"""

    def traverse(self, name, ignored):
        site = getParent(self.context, ISiteManager)
        if site is not None:
            manager = queryAdapter(site, IBannerManager, name)
            if manager is not None:
                return manager
        raise TraversalError('++banner++')


class BannerManagerContentsView(OrderedContainerBaseView):
    """Banner manager contents view"""

    implements(IBannerManagerContentsView)

    interface = IBannerImage

    @property
    def values(self):
        adapter = getAdapter(self.context, IBannerManager, self.name)
        if adapter is not None:
            return removeSecurityProxy(adapter).values()
        return []

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('id')
        if oid:
            intids = getUtility(IIntIds)
            target = intids.getObject(int(oid))
            parent = traversing_api.getParent(target)
            del parent[traversing_api.getName(target)]
            return "OK"
        return "NOK"

    @ajax.handler
    def ajaxUpdateOrder(self):
        adapter = getAdapter(self.context, IBannerManager, self.name)
        self.updateOrder(adapter)


class IBannerManagerPreviewColumn(Interface):
    """Marker interface for resource container preview column"""

class BannerManagerPreviewColumn(Column):
    """Resource container preview column"""

    implements(IBannerManagerPreviewColumn)

    header = u''
    weight = 5
    cssClasses = { 'th': 'preview',
                   'td': 'preview' }

    def renderCell(self, item):
        image = IImage(item.image, None)
        if image is None:
            return u''
        display = IImageDisplay(image).getDisplay('64x64')
        return '''<img src="%s" alt="%s" />''' % (absoluteURL(display, self.request),
                                                  traversing_api.getName(image))


class BannerManagerContentsViewActionsColumnCellAdapter(object):

    adapts(IBannerImage, IZTFYBrowserLayer, IBannerManagerContentsView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column
        self.intids = getUtility(IIntIds)

    @property
    def content(self):
        klass = "ui-workflow ui-icon ui-icon-trash"
        result = '''<span class="%s" title="%s" onclick="$.ZTFY.form.remove(%d, this);"></span>''' % (klass,
                                                                                                      translate(_("Delete image"), context=self.request),
                                                                                                      self.intids.register(self.context))
        return result


#
# Top banner custom classes extensions
#

@adapter(ISiteManager)
@implementer(IBannerManager)
def TopBannerManagerFactory(context):
    return BannerManagerFactory(context, 'top')


class TopBannerContentsMenuItem(HPLSkinMenuItem):
    """TopBanner contents menu item"""

    title = _("Top banner")


class TopBannerContentsView(BannerManagerContentsView):
    """TopBanner manager contents view"""

    implements(ITopBannerImageAddFormMenuTarget)

    legend = _("Top banner images")
    name = 'top'


#
# Left banner custom classes extensions
#

@adapter(ISiteManager)
@implementer(IBannerManager)
def LeftBannerManagerFactory(context):
    return BannerManagerFactory(context, 'left')


class LeftBannerContentsMenuItem(HPLSkinMenuItem):
    """LeftBanner contents menu item"""

    title = _("Left banner")


class LeftBannerContentsView(BannerManagerContentsView):
    """TopBanner manager contents view"""

    implements(ILeftBannerImageAddFormMenuTarget)

    legend = _("Left banner images")
    name = 'left'


#
# Banner images management
#

class BannerImage(Persistent, Contained):
    """Banner image"""

    implements(IBannerImage)

    image = ImageProperty(IBannerImage['image'], klass=Image, img_klass=Image)


class BannerImageAddForm(DialogAddForm):
    """Banner image add form"""

    title = _("New banner image")
    legend = _("Adding new image")

    fields = field.Fields(IBannerImage)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager
    handle_upload = True

    def create(self, data):
        return BannerImage()

    def add(self, image):
        data = self.request.form.get('form.widgets.image')
        filename = None
        if hasattr(data, 'filename'):
            filename = translateString(data.filename, escapeSlashes=True, forceLower=False, spaces='-')
            if filename in self.context:
                index = 2
                name = '%s-%d' % (filename, index)
                while name in self.context:
                    index += 1
                    name = '%s-%d' % (filename, index)
                filename = name
        if not filename:
            index = 1
            filename = 'image-%d' % index
            while filename in self.context:
                index += 1
                filename = 'image-%d' % index
        self.context[filename] = image


class BannerImageAddMenuItem(HPLSkinDialogMenuItem):
    """Banner image add menu"""

    title = _(":: Add image...")
    target = BannerImageAddForm


class TopBannerImageAddForm(BannerImageAddForm):

    parent_view = TopBannerContentsView


class LeftBannerImageAddForm(BannerImageAddForm):

    parent_view = LeftBannerContentsView


class BannerImageIndexView(BrowserPage):
    """Banner image default view"""

    def __call__(self):
        return queryMultiAdapter((self.context.image, self.request), Interface, 'index.html')()
