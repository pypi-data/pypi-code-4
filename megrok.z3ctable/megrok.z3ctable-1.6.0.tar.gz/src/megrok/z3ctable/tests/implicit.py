"""
Implicit is sometimes readable
==============================

In this example, we are going to demonstrate the implicit link between a table 
and a column, using auto resolving directives. Instead of directly declaring
the context and the table used to fetch a column, we resolve them by looking
into the module. Here, the column will automatically be register for the table
'SimpleTable' and the context 'DummyContainer' as they are the only possible
values in the module for these directives. This behavior, of course, can be
overriden by an explicit declaration of the directives at the class level.

  >>> from zope.publisher.browser import TestRequest
  
  >>> mongo = DummyContainer()
  >>> mongo['useless'] = object()
  
  >>> silly_table = SimpleTable(mongo, TestRequest())
  >>> silly_table.update()
  >>> print silly_table.render()
    <table>
      <thead>
        <tr>
          <th class="sorted-on ascending">Mongo</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="sorted-on ascending">I'm dumb</td>
        </tr>
      </tbody>
    </table>


To be sure that our column doesn't exist for any other context, we try to
render the table using another context::

  >>> john = Container()
  >>> empty_table = SimpleTable(john, TestRequest())
  >>> empty_table.update()
  >>> empty_table.render()
  u''

The table is empty : no column is registered for this context.
We can make the same test for the table::

  >>> class AnotherTable(Table):
  ...   '''Another table'''
  >>> empty_table = AnotherTable(mongo, TestRequest())
  >>> empty_table.update()
  >>> empty_table.render()
  u''
  
"""

import grokcore.component as grok
from megrok.z3ctable import Table, Column
from megrok.z3ctable.tests import Container


class DummyContainer(Container):
    """A stupid context
    """

class SimpleTable(Table):
    """A simple table
    """

class DumbColumn(Column):
    grok.name('firstColumn') 

    weight = 10
    header = u'Mongo'

    def renderCell(self, item):
        return u"I'm dumb"
