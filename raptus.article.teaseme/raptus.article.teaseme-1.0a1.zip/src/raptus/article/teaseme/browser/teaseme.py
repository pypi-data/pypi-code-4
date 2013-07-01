from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.teaser.interfaces import ITeaser

WYSIWYG = False
try:
    from raptus.article.additionalwysiwyg.interfaces import IWYSIWYG
    WYSIWYG = True
except ImportError:
    pass


class ITeaseme(interface.Interface):
    """ Marker interface for the teaseme viewlet
    """


class Component(object):
    """ Component which shows the article teased
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Teaser')
    description = _(u'The articles image filling the whole page width and title and description on top of it.')
    image = '++resource++teaseme.gif'
    interface = ITeaseme
    viewlet = 'raptus.article.teaseme'

    def __init__(self, context):
        self.context = context


class Viewlet(ViewletBase):
    """ Viewlet showing article teased
    """
    index = ViewPageTemplateFile('teaseme.pt')
    css_class = 'teaseme'

    @property
    @memoize
    def image(self):
        return ITeaser(self.context).getTeaserURL()

    @property
    @memoize
    def thumb(self):
        return '%s/image_thumb' % self.context.absolute_url()

    @property
    @memoize
    def wysiwyg(self):
        if not WYSIWYG:
            return
        props = getToolByName(self.context, 'portal_properties').raptus_article
        if not props.getProperty('teaseme_wysiwyg', False):
            return
        return IWYSIWYG(self.context).getAdditionalText()


def hideTitleAndDescription(object, component, event):
    object.setHideTitle(True)
    object.setHideDescription(True)
