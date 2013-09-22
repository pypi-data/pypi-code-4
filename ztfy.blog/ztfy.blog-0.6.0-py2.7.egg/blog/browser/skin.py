### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
import copy

# import Zope3 interfaces
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.schema.interfaces import IText

# import local interfaces
from ztfy.blog.interfaces.resource import IResourceContainerTarget
from ztfy.file.browser.widget.interfaces import IHTMLWidgetSettings
from ztfy.skin.interfaces import ISkinnable, IBaseForm
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYFrontLayer

# import Zope3 packages
from z3c.form import widget
from z3c.form.browser.select import SelectWidget
from zope.component import adapter, adapts, queryUtility, queryMultiAdapter
from zope.interface import implements, implementer
from zope.publisher.browser import applySkin
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.utils.traversing import getParent

from ztfy.blog import _


#
# Skin selection widget
#

class SkinSelectWidget(SelectWidget):
    noValueMessage = _("(inherit parent skin)")

def SkinSelectWidgetFactory(field, request):
    return widget.FieldWidget(field, SkinSelectWidget(request))


#
# HTML widget
#

@adapter(IText, IBaseForm, IZTFYBrowserLayer)
@implementer(IHTMLWidgetSettings)
def  HTMLWidgetAdapterFactory(field, form, request):
    """Create widget adapter matching content's applied skin"""
    settings = None
    target = getParent(form.context, ISkinnable)
    if target is not None:
        skin_name = ISkinnable(target).getSkin()
        if not skin_name:
            skin_name = 'ZBlog'
        skin = queryUtility(IBrowserSkinType, skin_name)
        if skin is not None:
            fake = copy.copy(request)
            applySkin(fake, skin)
            settings = queryMultiAdapter((field, form, fake), IHTMLWidgetSettings)
    return settings


class HTMLWidgetAdapter(object):
    """HTML widget settings adapter"""

    adapts(IText, IBaseForm, IZTFYFrontLayer)
    implements(IHTMLWidgetSettings)

    def __init__(self, field, form, request):
        self.field = field
        self.form = form
        self.request = request

    mce_invalid_elements = 'h1,h2'

    @property
    def mce_external_image_list_url(self):
        target = getParent(self.form.context, IResourceContainerTarget)
        if target is not None:
            return '%s/@@getImagesList.js' % absoluteURL(target, self.request)
        return None

    @property
    def mce_external_link_list_url(self):
        target = getParent(self.form.context, IResourceContainerTarget)
        if target is not None:
            return '%s/@@getLinksList.js' % absoluteURL(target, self.request)
        return None
