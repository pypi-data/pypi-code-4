"""
Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.site.hooks import getSite
  >>> root = getSite()
  >>> cont = Container()

and set a parent for the cont:

  >>> root['cont'] = cont

Now setup some items:

  >>> from megrok.z3ctable.tests import Content

  >>> cont[u'first'] = Content('First', 1)
  >>> cont[u'second'] = Content('Second', 2)
  >>> cont[u'third'] = Content('Third', 3)

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> table_view = getMultiAdapter((cont, TestRequest()), name=u'tableview')
  >>> print table_view()
  <table>
    <thead>
      <tr>
        <th class="sorted-on ascending">Name</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="sorted-on ascending">first</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">second</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">third</td>
      </tr>
    </tbody>
  </table>

  >>> tvwt = getMultiAdapter((cont, TestRequest()), name=u'tvwt')
  >>> print tvwt()
  <html>
   <body>
    <h1>This is my nice Table rendered in a template</h1>
    <table>
    <thead>
      <tr>
        <th class="sorted-on ascending">Name</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="sorted-on ascending">first</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">second</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">third</td>
      </tr>
    </tbody>
  </table>
   </body>
  </html>

table rendered in a layout with a template

  >>> tpil = getMultiAdapter((cont, TestRequest()), name=u'tablepageinlayout')
  >>> print tpil()
  <html>
   <body>
     <div class="layout"><div>
    <table>
    <thead>
      <tr>
        <th class="sorted-on ascending">Name</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="sorted-on ascending"></td>
        <td></td>
      </tr>
      <tr>
        <td class="sorted-on ascending"></td>
        <td></td>
      </tr>
      <tr>
        <td class="sorted-on ascending"></td>
        <td></td>
      </tr>
    </tbody>
  </table>
  </div> 
  </div>
   </body>
  </html>


table rendered in a layout with an render method

  >>> twr = getMultiAdapter((cont, TestRequest()), name=u'tablewithrender')
  >>> print twr()
  <html>
   <body>
     <div class="layout"><table>
    <thead>
      <tr>
        <th class="sorted-on ascending">Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="sorted-on ascending">first</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">second</td>
      </tr>
      <tr>
        <td class="sorted-on ascending">third</td>
      </tr>
    </tbody>
  </table></div>
   </body>
  </html>


"""

import grokcore.component as grok
from grokcore.layout import Layout
from zope.interface import Interface
from megrok.z3ctable.tests import Container
from megrok.z3ctable import (TableView, table, 
                             GetAttrColumn, NameColumn, TablePage)


class TableView(TableView):
    grok.context(Container)


class Name(NameColumn):
    grok.context(Interface)
    table(TableView)


class TW(TableView):
    grok.name('tvwt')
    grok.context(Container)


class NewName(NameColumn):
    grok.context(Interface)
    table(TW)


class TableLayout(Layout):
    grok.context(Interface)


class TablePageInLayout(TablePage):
    grok.context(Container)


class MyName(GetAttrColumn):
    grok.name('myname')
    grok.context(Interface)
    table(TablePageInLayout)
    header = u"Name"
    weight = 1 


class MyNumbers(GetAttrColumn):
    grok.name('mynumbers')
    grok.context(Interface)
    table(TablePageInLayout)
    header = u"Number"
    weight = 2


class TableWithRender(TablePage):
    grok.context(Container)

    def render(self):
        return self.renderTable()


class Title(NameColumn):
    """Display the name of the content item
    """
    grok.context(Interface)
    table(TableWithRender)
    header = u"Title"


def test_suite():
    from zope.testing import doctest
    from megrok.z3ctable.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite 
