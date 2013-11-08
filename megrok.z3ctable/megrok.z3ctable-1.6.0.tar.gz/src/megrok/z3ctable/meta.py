# -*- coding: utf-8 -*-

import martian
import grokcore.view
import megrok.z3ctable
import grokcore.component

from zope import component
from z3c.table.interfaces import ITable
from martian.util import scan_for_classes
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TableGrokker(martian.GlobalGrokker):
    """Grokker dedicated to find the table within a module.
    This allows to set implicit relationships between a table and a column.
    """
    martian.priority(991)

    def get_default(cls, component, module=None, **data):
        components = list(scan_for_classes(module, megrok.z3ctable.ITable))
        if len(components) == 0:
            return None
        elif len(components) == 1:
            component = components[0]
        else:
            return None
        return component

    def grok(self, name, module, module_info, config, **kw):
        factory = self.get_default(module, module)
        if factory is not None:
            megrok.z3ctable.table.set(module, factory)
        return True


class ColumnGrokker(martian.ClassGrokker):
    martian.priority(990)
    martian.component(megrok.z3ctable.components.Column)

    martian.directive(grokcore.component.name)
    martian.directive(grokcore.component.context)
    martian.directive(megrok.z3ctable.table, default=ITable)
    martian.directive(grokcore.component.provides)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)

    def execute(self, factory, config, layer, context, table, provides, name):
        for_ = (context, layer, table)
        config.action(
            discriminator=('adapter', for_, provides, name),
            callable=component.provideAdapter,
            args=(factory, for_, provides, name),
            )
        return True
