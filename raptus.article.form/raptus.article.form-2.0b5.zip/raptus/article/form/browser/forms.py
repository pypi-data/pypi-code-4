from zope import interface, component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.form.interfaces import IForms as IFormsProvider

class IForms(interface.Interface):
    """ Marker interface for the forms viewlet
    """

class Component(object):
    """ Component which shows the forms contained in the article
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Forms')
    description = _(u'List of forms contained in the article.')
    image = '++resource++forms.gif'
    interface = IForms
    viewlet = 'raptus.article.forms'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the forms contained in the article
    """
    index = ViewPageTemplateFile('forms.pt')
    
    @property
    @memoize
    def forms(self):
        items = []
        provider = IFormsProvider(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getForms())
        for item in items:
            form = self.context.restrictedTraverse('%s/@@embedded' % item['id'])
            form.prefix = item['id']
            item['form'] = form
        return items
