"""
Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.site.hooks import getSite
  >>> root = getSite()
  >>> container = Container()

and set a parent for the container:

  >>> root['container'] = container

Now setup some items:

  >>> container[u'first'] = Content('First', 1)
  >>> container[u'second'] = Content('Second', 2)
  >>> container[u'third'] = Content('Third', 3)

  >>> from zope.publisher.browser import TestRequest
  >>> table = Table(container, TestRequest())

Start with a very Basic Example

  >>> from megrok.z3ctable import ITable
  >>> ITable.providedBy(table)
  True

  >>> from z3c.table.interfaces import ITable as IOriginalTable
  >>> ITable is IOriginalTable
  True

  >>> table.update()
  >>> table.render()
  u''

Work on a table with some Columns

  >>> mytable = MyTable(container, TestRequest())
  >>> IMyTable.providedBy(mytable)
  True

  >>> mytable.update()
  >>> print mytable.render()
  <table>
    <thead>
      <tr>
        <th class="sorted-on ascending">Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="sorted-on ascending">Title: First</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">Title: Second</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">Title: Third</td>
      </tr>
    </tbody>
  </table>

Name Column, GetAttrColumn, LinkColumn and CheckboxColumn

  >>> nametable = NameTable(container, TestRequest())
  >>> nametable.update()
  >>> print nametable.render()
  <table>
    <thead>
      <tr>
        <th class="sorted-on ascending">X</th>
        <th>Name</th>
        <th>Number</th>
        <th>edit</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="sorted-on ascending"><input type="checkbox" class="checkbox-widget" name="table-checkBox-0-selectedItems" value="first"  /></td>
        <td>first</td>
        <td>1</td>
        <td><a href="http://127.0.0.1/container/first/edit">edit this item</a></td>
      </tr>
      <tr>
        <td class="sorted-on ascending"><input type="checkbox" class="checkbox-widget" name="table-checkBox-0-selectedItems" value="second"  /></td>
        <td>second</td>
        <td>2</td>
        <td><a href="http://127.0.0.1/container/second/edit">edit this item</a></td>
      </tr>
      <tr>
        <td class="sorted-on ascending"><input type="checkbox" class="checkbox-widget" name="table-checkBox-0-selectedItems" value="third"  /></td>
        <td>third</td>
        <td>3</td>
        <td><a href="http://127.0.0.1/container/third/edit">edit this item</a></td>
      </tr>
    </tbody>
  </table>



Custom Values for the Table

  >>> customValues = CustomValues(container, TestRequest())
  >>> customValues.update()
  >>> print customValues.render()
  <table>
    <thead>
      <tr>
        <th class="sorted-on ascending">Name</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="sorted-on ascending"></td>
      </tr>
      <tr>
        <td class="sorted-on ascending"></td>
      </tr>
    </tbody>
  </table>
  
"""

import grokcore.component as grok
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from megrok.z3ctable.tests import Container, Content
from megrok.z3ctable import (Table, Column, NameColumn,
                             GetAttrColumn, CheckBoxColumn,
			     LinkColumn, Values, table)


class IMyTable(Interface):
    """Marker Interface for MyTable
    """


class MyTable(Table):
    grok.implements(IMyTable)


class Title(Column):
    grok.name('firstColumn') 
    grok.context(Interface)
    table(IMyTable)

    weight = 10
    header = u'Title'

    def renderCell(self, item):
        return u'Title: %s' % item.title


class NameTable(Table):
    pass


class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(Interface)
    table(NameTable)
    weight = 0


class Name(NameColumn):
    grok.name('secondColumn') 
    grok.context(Interface)
    table(NameTable)
    weight = 1


class Number(GetAttrColumn):
    grok.name('numberColumn')
    grok.context(Interface)
    table(NameTable)
    attrName = u"number"
    weight = 2 
    header = u"Number"


class Link(LinkColumn):
    grok.name('link')
    grok.context(Interface)
    table(NameTable)
    weight = 3
    header = u"edit"
    linkName = u"edit"
    linkContent = u"edit this item"
    

class CustomValues(Table):
    pass


class MyValues(Values):
    grok.adapts(Container, IBrowserRequest, CustomValues)

    @property
    def values(self):
        return [Content('eins', 1), Content('zwei', 2)]


class CustomName(GetAttrColumn):
    grok.name('nColumn') 
    grok.context(Interface)
    table(CustomValues)
    attrName = u"name"
    weight = 1
    header = u"Name"
