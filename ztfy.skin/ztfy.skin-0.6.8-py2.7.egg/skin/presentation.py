### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
from hurry.query.interfaces import IQuery
from z3c.json.interfaces import IJSONWriter
from z3c.language.switch.interfaces import II18n
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.skin.interfaces import ISkinnable, IPresentationTarget, IPresentationForm, IBaseIndexView

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.template.template import getLayoutTemplate
from zope.component import queryUtility, queryMultiAdapter, getUtility
from zope.interface import implements
from zope.publisher.skinnable import applySkin
from zope.traversing import namespace

# import local packages
from ztfy.skin.form import DialogEditForm
from ztfy.skin.page import TemplateBasedPage
from ztfy.utils.catalog.index import Text
from ztfy.utils.traversing import getParent

#
# Presentation management classes
#

class PresentationNamespaceTraverser(namespace.view):
    """++presentation++ namespace"""

    def getSkin(self):
        skinnable = getParent(self.context, ISkinnable)
        if skinnable is None:
            return None
        skin_name = skinnable.getSkin()
        if skin_name is None:
            return None
        return queryUtility(IBrowserSkinType, skin_name)

    def traverse(self, name, ignored):
        skin = self.getSkin()
        if skin is None:
            raise TraversalError('++presentation++')
        fake = copy.copy(self.request)
        applySkin(fake, skin)
        adapter = queryMultiAdapter((self.context, fake), IPresentationTarget)
        if adapter is not None:
            try:
                return adapter.target_interface(self.context)
            except:
                pass
        raise TraversalError('++presentation++')


class BasePresentationEditForm(DialogEditForm):
    """Presentation edit form"""

    implements(IPresentationForm)

    layout = getLayoutTemplate()

    def __init__(self, context, request):
        super(BasePresentationEditForm, self).__init__(context, request)
        skin = self.getSkin()
        if skin is None:
            raise NotFound(self.context, self.name, self.request)
        fake = copy.copy(self.request)
        applySkin(fake, skin)
        adapter = queryMultiAdapter((self.context, fake, self), IPresentationTarget)
        if adapter is None:
            adapter = queryMultiAdapter((self.context, fake), IPresentationTarget)
        if adapter is None:
            raise NotFound(self.context, self.name, self.request)
        self.interface = adapter.target_interface

    def getContent(self):
        return self.interface(self.context)

    @property
    def fields(self):
        return field.Fields(self.interface)

    def getSkin(self):
        skinnable = getParent(self.context, ISkinnable)
        if skinnable is None:
            return None
        skin_name = skinnable.getSkin()
        if skin_name is None:
            return None
        return queryUtility(IBrowserSkinType, skin_name)

    @ajax.handler
    def ajaxEdit(self):
        return super(BasePresentationEditForm, self).ajaxEdit(self)

    @ajax.handler
    def ajaxSearch(self):
        writer = getUtility(IJSONWriter)
        title = self.request.form.get('title')
        if not title:
            return writer.write(None)
        query = getUtility(IQuery)
        intids = getUtility(IIntIds)
        result = []
        for obj in query.searchResults(Text(('Catalog', 'title'),
                                            { 'query': title + '*',
                                              'ranking': True })):
            result.append({ 'oid': intids.register(obj),
                            'title': II18n(obj).queryAttribute('title') })
        return writer.write(result)


#
# Base index view
#

class BaseIndexView(TemplateBasedPage):
    """Base index view"""

    implements(IBaseIndexView)

    presentation = None

    def update(self):
        super(BaseIndexView, self).update()
        adapter = queryMultiAdapter((self.context, self.request, self), IPresentationTarget)
        if adapter is None:
            adapter = queryMultiAdapter((self.context, self.request), IPresentationTarget)
        if adapter is not None:
            interface = adapter.target_interface
            self.presentation = interface(self.context)
