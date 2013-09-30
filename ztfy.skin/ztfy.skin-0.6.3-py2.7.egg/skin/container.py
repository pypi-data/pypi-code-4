### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from z3c.template.interfaces import IPageTemplate
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.base.interfaces.container import IOrderedContainer
from ztfy.skin.interfaces import IContainedDefaultView, IDefaultView
from ztfy.skin.interfaces.container import IOrderedContainerBaseView, IContainerAddFormMenuTarget, \
                                           IIdColumn, INameColumn, ITitleColumn, IStatusColumn, IActionsColumn, \
                                           IContainerTableViewTitleCell, IContainerTableViewStatusCell, \
                                           IContainerTableViewActionsCell, IOrderedContainerSorterColumn, IContainerBaseView

# import Zope3 packages
from z3c.formjs import ajax
from z3c.table.batch import BatchProvider
from z3c.table.column import Column, FormatterColumn, GetAttrColumn
from z3c.table.table import Table
from z3c.template.template import getViewTemplate, getPageTemplate
from zope.i18n import translate
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.interface import implements
from zope.traversing.api import getName

# import local packages
from ztfy.jqueryui import jquery_ui_css, jquery_jsonrpc, jquery_ui_base, jquery_tipsy
from ztfy.skin.menu import MenuItem
from ztfy.skin.page import BaseBackView, TemplateBasedPage
from ztfy.utils.timezone import tztime

from ztfy.skin import _


class ContainerContentsViewMenu(MenuItem):
    """Container contents menu"""

    title = _("Contents")


class OrderedContainerSorterColumn(Column):

    implements(IOrderedContainerSorterColumn)

    header = u''
    weight = 1
    cssClasses = { 'th': 'sorter',
                   'td': 'sorter' }

    def renderCell(self, item):
        return '<img class="handler" src="/--static--/ztfy.skin/img/sort.png" />'


class IdColumn(Column):

    implements(IIdColumn)

    weight = 0
    cssClasses = { 'th': 'hidden',
                   'td': 'hidden id' }

    def renderHeadCell(self):
        return u''

    def renderCell(self, item):
        return getName(item)


class NameColumn(IdColumn):

    implements(INameColumn)

    cssClasses = {}

    def renderCell(self, item):
        result = getName(item)
        adapter = queryMultiAdapter((item, self.request, self.table), IContainedDefaultView)
        if adapter is None:
            adapter = queryMultiAdapter((item, self.request, self.table), IDefaultView)
        if adapter is not None:
            result = '<a href="%s">%s</a>' % (adapter.getAbsoluteURL(), result)
        return result


class TitleColumn(Column):

    implements(ITitleColumn)

    header = _("Title")
    weight = 10
    cssClasses = { 'td': 'title' }

    def renderCell(self, item):
        adapter = queryMultiAdapter((item, self.request, self.table, self), IContainerTableViewTitleCell)
        prefix = (adapter is not None) and adapter.prefix or ''
        before = (adapter is not None) and adapter.before or ''
        after = (adapter is not None) and adapter.after or ''
        suffix = (adapter is not None) and adapter.suffix or ''
        i18n = II18n(item, None)
        if i18n is not None:
            title = i18n.queryAttribute('title', request=self.request)
        else:
            title = IZopeDublinCore(item).title
        result = "%s%s%s" % (before, title or '{{ ' + getName(item) + ' }}', after)
        adapter = queryMultiAdapter((item, self.request, self.table), IContainedDefaultView)
        if adapter is None:
            adapter = queryMultiAdapter((item, self.request, self.table), IDefaultView)
        if adapter is not None:
            url = adapter.getAbsoluteURL()
            if url:
                result = '<a href="%s">%s</a>' % (url, result)
        return '%s%s%s' % (prefix, result, suffix)


class CreatedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Created')
    weight = 100
    cssClasses = { 'td': 'date' }

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'created'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(tztime(value))
        return value


class ModifiedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Modified')
    weight = 110
    cssClasses = { 'td': 'date' }

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'modified'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(tztime(value))
        return value


class StatusColumn(Column):

    implements(IStatusColumn)

    header = _("Status")
    weight = 200
    cssClasses = { 'td': 'status' }

    def renderCell(self, item):
        adapter = queryMultiAdapter((item, self.request, self.table, self), IContainerTableViewStatusCell)
        if adapter is not None:
            return adapter.content
        return ''


class ActionsColumn(Column):

    implements(IActionsColumn)

    header = _("Actions")
    weight = 210
    cssClasses = { 'td': 'actions' }

    def renderCell(self, item):
        adapter = queryMultiAdapter((item, self.request, self.table, self), IContainerTableViewActionsCell)
        if adapter is not None:
            return adapter.content
        return ''


class ContainerBatchProvider(BatchProvider):
    """Custom container batch provider"""

    batchSpacer = u'<a>...</a>'


class BaseContainerBaseView(TemplateBasedPage, Table):
    """Container-like base view"""

    implements(IContainerBaseView)

    legend = _("Container's content")
    empty_message = _("This container is empty")

    data_attributes = {}

    batchSize = 25
    startBatchingAt = 25

    output = getViewTemplate()

    def __init__(self, context, request):
        super(BaseContainerBaseView, self).__init__(context, request)
        Table.__init__(self, context, request)

    @property
    def title(self):
        result = None
        i18n = II18n(self.context, None)
        if i18n is not None:
            result = II18n(self.context).queryAttribute('title', request=self.request)
        if result is None:
            dc = IZopeDublinCore(self.context, None)
            if dc is not None:
                result = dc.title
        if not result:
            result = '{{ %s }}' % getName(self.context)
        return result

    def getCSSClass(self, element, cssClass=None):
        result = super(BaseContainerBaseView, self).getCSSClass(element, cssClass)
        result += ' ' + ' '.join(('data-%s=%s' % (k, v) for k, v in self.data_attributes.items()))
        return result

    @property
    def empty_value(self):
        return translate(self.empty_message, context=self.request)

    def update(self):
        TemplateBasedPage.update(self)
        Table.update(self)
        jquery_tipsy.need()
        jquery_ui_css.need()
        jquery_jsonrpc.need()


class ContainerBaseView(BaseBackView, BaseContainerBaseView):
    """Back-office container base view"""

    def update(self):
        BaseBackView.update(self)
        BaseContainerBaseView.update(self)


class OrderedContainerBaseView(ajax.AJAXRequestHandler, ContainerBaseView):

    implements(IOrderedContainerBaseView, IContainerAddFormMenuTarget)

    sortOn = None
    interface = None
    container_interface = IOrderedContainer

    batchSize = 10000
    startBatchingAt = 10000

    cssClasses = { 'table': 'orderable' }

    def update(self):
        super(OrderedContainerBaseView, self).update()
        jquery_ui_base.need()
        jquery_jsonrpc.need()

    @ajax.handler
    def ajaxUpdateOrder(self, *args, **kw):
        self.updateOrder()

    def updateOrder(self, context=None):
        ids = self.request.form.get('ids', [])
        if ids:
            if context is None:
                context = self.context
            container = self.container_interface(context)
            container.updateOrder(ids, self.interface)


class InnerContainerBaseView(Table):
    """A container table displayed inside another view"""

    template = getPageTemplate()

    data_attributes = {}

    def __init__(self, view, request):
        Table.__init__(self, view.context, request)
        self.__parent__ = view
        self.__name__ = u''

    def getCSSClass(self, element, cssClass=None):
        result = super(InnerContainerBaseView, self).getCSSClass(element, cssClass)
        result += ' ' + ' '.join(('data-%s=%s' % (k, v) for k, v in self.data_attributes.items()))
        return result

    def render(self):
        if self.template is None:
            template = getMultiAdapter((self, self.request), IPageTemplate)
            return template(self)
        return self.template()
