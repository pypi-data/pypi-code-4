from string import Template
from urllib import urlencode

try:
    from zope.app.schema.vocabulary import IVocabularyFactory
except ImportError:
    # plone 4.1
    from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements
from zope.formlib import form
from zope.schema import List, Choice, TextLine

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.blogging.interfaces import IEntryMarker
from collective.blogging import _
from collective.blogging import SHARING_PROVIDERS

class ProvidersVocabulary(object):
    """"""
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(p, p, p)
                    for p in SHARING_PROVIDERS.keys()]
        return SimpleVocabulary(items)

ProvidersVocabularyFactory = ProvidersVocabulary()

class ISharePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    name = TextLine(
        required = False,
        title = _(u"Portlet title"),
        description = _(u"Enter portlet tile.")
    )

    restrict_types = List(
        required = False,
        title = _(u"Select types"),
        description = _(u"Enable portlet by content types wich entries are based on."),
        value_type = Choice(vocabulary =
            'plone.app.vocabularies.ReallyUserFriendlyTypes'),
    )
    
    providers = List(
        required = True,
        title = _(u"Providers"),
        description = _(u"Select enabled sharing services."),
        value_type = Choice(vocabulary =
            'collective.blogging.SharingProviders'),
    )

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISharePortlet)
    
    name = u''
    restrict_types = []
    providers = []
    
    def __init__(self, name=u'', restrict_types=[], providers=[]):
        self.name = name
        self.restrict_types = restrict_types
        self.providers = providers
    
    @property
    def title(self):
        return self.name or _(u'Share post')

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('share.pt')
    
    @property
    def available(self):
        if not IEntryMarker.providedBy(self.context):
            return False
        if self.context.portal_type not in self.data.restrict_types:
            return False
        return True

    def header(self):
        return self.data.name or _(u'Share post')
    
    def providers(self):
        result = []
        obj = aq_inner(self.context)
        url = obj.absolute_url()
        title = obj.title
        for p in self.data.providers:
            p_url = Template(SHARING_PROVIDERS[p]['url']).safe_substitute(url=url, title=title)
            result.append({
                'id': p,
                'logo':SHARING_PROVIDERS[p]['logo'],
                'url':p_url
            })
        return result

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISharePortlet)
    
    label = _(u"Add Share Entry portlet")
    description = _(u"This portlet renders link(s) to share an entry.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(ISharePortlet)

    label = _(u"Edit Share Entry portlet")
    description = _(u"This portlet renders link(s) to share an entry.")
