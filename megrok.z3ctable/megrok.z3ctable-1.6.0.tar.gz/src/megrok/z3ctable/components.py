# -*- coding: utf-8 -*-

import grokcore.layout as layout
import grokcore.view as view
import grokcore.component as grok
from z3c.table import table, column, interfaces


class Table(table.Table):
    """A table.
    """


class TableView(view.View, Table):
    """A view that renders a Table.
    """
    grok.baseclass()

    def __init__(self, context, request):
        view.View.__init__(self, context, request)
        Table.__init__(self, context, request)

    def update(self):
        Table.update(self)

    def render(self):
        return Table.render(self)

    render.base_method = True


class TablePage(layout.Page, Table):
    """A Page that renders a Table.
    """
    grok.baseclass()

    def __init__(self, context, request):
        layout.Page.__init__(self, context, request)
        Table.__init__(self, context, request)

    def update(self):
        Table.update(self)

    def render(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self.template.render(self)
        return self.renderTable()

    render.base_method = True


class Column(column.Column):
    """ A basic Column
    """
    grok.baseclass()
    grok.provides(interfaces.IColumn)


class NameColumn(column.NameColumn, Column):
    """Name Column
    """
    grok.baseclass()


class GetAttrColumn(column.GetAttrColumn, Column):
    """GetAttr Column
    """
    grok.baseclass()


class CheckBoxColumn(column.CheckBoxColumn, Column):
    """CheckBox Column
    """
    grok.baseclass()


class LinkColumn(column.LinkColumn, Column):
    """Link Column
    """
    grok.baseclass()


class ModifiedColumn(column.ModifiedColumn, Column):
    """Modified Column
    """
    grok.baseclass()


class Values(grok.MultiAdapter):
    """Adapter for custom Value Implementation
    """
    grok.baseclass()
    grok.provides(interfaces.IValues)

    def __init__(self, context, request, table):
        self.context = context
        self.request = request
        self.table = table

    @property
    def values(self):
        return NotImplementedError(
            """Your class must override the `values` method.""")


__all__ = ('Table', 'TableView', 'TablePage',
           'NameColumn', 'Column', 'GetAttrColumn',
           'CheckBoxColumn', 'LinkColumn', 'Values',
           'ModifiedColumn')
