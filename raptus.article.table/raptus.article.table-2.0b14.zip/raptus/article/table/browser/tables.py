from Acquisition import aq_inner
from zope import interface, component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.table.interfaces import ITables

class ITablesLeft(interface.Interface):
    """ Marker interface for the tables left viewlet
    """

class ComponentLeft(object):
    """ Component which lists the tables on the left side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Tables left')
    description = _(u'List of tables contained in the article on the left side.')
    image = '++resource++tables_left.gif'
    interface = ITablesLeft
    viewlet = 'raptus.article.table.left'
    
    def __init__(self, context):
        self.context = context

class ViewletLeft(ViewletBase):
    """ Viewlet listing the tables on the left side
    """
    index = ViewPageTemplateFile('tables.pt')
    css_class = "componentLeft tables-left"
    component = "tables.left"
    
    def _class(self, brain, i, l):
        cls = []
        if i == 0:
            cls.append('first')
        if i == l-1:
            cls.append('last')
        if i % 2 == 0:
            cls.append('odd')
        if i % 2 == 1:
            cls.append('even')
        return ' '.join(cls)
    
    @property
    @memoize
    def tables(self):
        provider = ITables(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getTables(component=self.component), self.component)
        i = 0
        l = len(items)
        for item in items:
            table = component.getMultiAdapter((item['obj'], self.request), name='table')()
            if not table:
                continue
            item.update({'uid': item['brain'].UID,
                         'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'class': self._class(item['brain'], i, l),
                         'table': table})
            i += 1
        return items

class ITablesRight(interface.Interface):
    """ Marker interface for the tables right viewlet
    """

class ComponentRight(object):
    """ Component which lists the tables on the right side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Tables right')
    description = _(u'List of tables contained in the article on the right side.')
    image = '++resource++tables_right.gif'
    interface = ITablesRight
    viewlet = 'raptus.article.table.right'
    
    def __init__(self, context):
        self.context = context

class ViewletRight(ViewletLeft):
    """ Viewlet listing the tables on the right side
    """
    css_class = "componentRight tables-right"
    component = "tables.right"

class ITablesFull(interface.Interface):
    """ Marker interface for the tables full viewlet
    """

class ComponentFull(object):
    """ Component which lists the tables over the whole width
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Tables')
    description = _(u'List of tables contained in the article over the whole width.')
    image = '++resource++tables_full.gif'
    interface = ITablesFull
    viewlet = 'raptus.article.table.full'
    
    def __init__(self, context):
        self.context = context

class ViewletFull(ViewletLeft):
    """ Viewlet listing the tables over the whole width
    """
    css_class = "componentFull tables-full"
    component = "tables.full"
    
