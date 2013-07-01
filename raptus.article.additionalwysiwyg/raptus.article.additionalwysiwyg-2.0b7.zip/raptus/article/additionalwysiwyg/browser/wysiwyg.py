from Acquisition import aq_inner
from zope import interface, component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.additionalwysiwyg.interfaces import IWYSIWYG


class IWYSIWYGLeft(interface.Interface):
    """ Marker interface for the WYSIWYG left viewlet
    """


class ComponentLeft(object):
    """ Component which shows the additional WYSIWYG of an article on the left side
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Additional text left')
    description = _(u'Additional text on the left side.')
    image = '++resource++wysiwyg_left.gif'
    interface = IWYSIWYGLeft
    viewlet = 'raptus.article.wysiwyg.left'

    def __init__(self, context):
        self.context = context


class ViewletLeft(ViewletBase):
    """ Viewlet showing the additional WYSIWYG of an article on the left side
    """
    index = ViewPageTemplateFile('wysiwyg.pt')
    css_class = "wysiwyg componentLeft wysiwyg-left"

    @property
    @memoize
    def text(self):
        provider = IWYSIWYG(self.context)
        return provider.getAdditionalText()


class IWYSIWYGRight(interface.Interface):
    """ Marker interface for the WYSIWYG right viewlet
    """


class ComponentRight(object):
    """ Component which shows the additional WYSIWYG of an article on the right side
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Additional text right')
    description = _(u'Additional text on the right side.')
    image = '++resource++wysiwyg_right.gif'
    interface = IWYSIWYGRight
    viewlet = 'raptus.article.wysiwyg.right'

    def __init__(self, context):
        self.context = context


class ViewletRight(ViewletLeft):
    """ Viewlet showing the additional WYSIWYG of an article on the right side
    """
    css_class = "wysiwyg componentRight wysiwyg-right"


class IWYSIWYGFull(interface.Interface):
    """ Marker interface for the WYSIWYG full viewlet
    """


class ComponentFull(object):
    """ Component which shows the additional WYSIWYG of an article over the whole width
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Additional text')
    description = _(u'Additional text over the whole width.')
    image = '++resource++wysiwyg_full.gif'
    interface = IWYSIWYGFull
    viewlet = 'raptus.article.wysiwyg.full'

    def __init__(self, context):
        self.context = context


class ViewletFull(ViewletLeft):
    """ Viewlet showing the additional WYSIWYG of an article over the whole width
    """
    css_class = "wysiwyg wysiwyg-full"


class IWYSIWYGTop(interface.Interface):
    """ Marker interface for the WYSIWYG top viewlet
    """


class ComponentTop(object):
    """ Component which shows the additional WYSIWYG of an article on top
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Additional text top')
    description = _(u'Additional text on top.')
    image = '++resource++wysiwyg_top.gif'
    interface = IWYSIWYGTop
    viewlet = 'raptus.article.wysiwyg.top'

    def __init__(self, context):
        self.context = context


class ViewletTop(ViewletLeft):
    """ Viewlet showing the additional WYSIWYG of an article on the bottom
    """
    css_class = "wysiwyg wysiwyg-top"


class IWYSIWYGBottom(interface.Interface):
    """ Marker interface for the WYSIWYG bottom viewlet
    """


class ComponentBottom(object):
    """ Component which shows the additional WYSIWYG of an article on the bottom
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Additional text bottom')
    description = _(u'Additional text on the bottom.')
    image = '++resource++wysiwyg_bottom.gif'
    interface = IWYSIWYGBottom
    viewlet = 'raptus.article.wysiwyg.bottom'

    def __init__(self, context):
        self.context = context


class ViewletBottom(ViewletLeft):
    """ Viewlet showing the additional WYSIWYG of an article on the bottom
    """
    css_class = "wysiwyg wysiwyg-bottom"
