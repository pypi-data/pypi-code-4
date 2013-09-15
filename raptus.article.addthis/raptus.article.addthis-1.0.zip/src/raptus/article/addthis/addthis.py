from zope import interface, component
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from raptus.article.core import interfaces
from raptus.article.addthis.interfaces import IAddthis
from Products.CMFPlone.utils import getToolByName

from raptus.article.addthis import articleMessageFactory as _


class ComponentAddthis(object):
    """ Component which shows a booking form on the bottom
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)

    title = _(u'addthis_title', default=u'Share on social networks')
    description = _(u'addthis_help', default=u'Show links for sharing this page on facebook, twitter, ...')
    image = '++resource++addthis.gif'
    interface = IAddthis
    viewlet = 'raptus.article.addthis'

    def __init__(self, context):
        self.context = context


class Addthis(ViewletBase):
    """ Viewlet showing the addthis integration
    """

    index = ViewPageTemplateFile('addthis.pt')
    component = "addthis"

    @property
    def show(self):
        props = getToolByName(self.context, 'portal_properties').raptus_article
        return props.getProperty('addthis_active', True)
    
    @property
    def addthis_code(self):
        props = getToolByName(self.context, 'portal_properties').raptus_article
        
        return props.getProperty('addthis_code', '')
        
        