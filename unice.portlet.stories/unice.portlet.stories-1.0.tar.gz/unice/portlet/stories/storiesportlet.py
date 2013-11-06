#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

try:
    from Products.LinguaPlone.interfaces import ITranslatable
    LINGUAPLONE_SUPPORT = True
except ImportError:
    # Linguaplone not installed
    LINGUAPLONE_SUPPORT = False

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from plone.memoize import instance

from unice.portlet.stories import StoriesPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

class IStoriesPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Stories portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )

    stories = schema.Choice(title=_(u"Elément à afficher"),
        required=True,
        source=SearchableTextSourceBinder(
            {},
            default_query='path:'
        )
    )

    item_display = schema.List(
        title=_(u'Informations à afficher'),
        description=_('help_item_display',
                      default=u"Sélectionner les informations de l'élément sélectionné à afficher"),
        value_type=schema.Choice(
            vocabulary='unice.portlet.stories.item_display_vocabulary',
        ),
        default=[u'date', u'image', u'description', u'body'],
        required=False,
    )

    more_text = schema.TextLine(
        title=_(u'Texte du lien "Plus d\'informations"'),
        description=_('help_more_text',
                      default=u"Laisser vide pour masquer le footer du portlet"),
        default=u'',
        required=False,
    )

    extra_id = schema.TextLine(
        title=_(u'Identifiant CSS à ajouter au portlet'),
        description=_('help_extra_id',
                      default=u""),
        default=u'',
        required=False,
    )
    extra_css = schema.TextLine(
        title=_(u'Classes CSS à ajouter au portlet'),
        description=_('help_extra_css',
                      default=u""),
        default=u'',
        required=False,
    )

    omit_header = schema.Bool(
        title=_(u"Masquer le header du portlet"),
        description=_('help_omit_header',
                      default=u""),
        required=True,
        default=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IStoriesPortlet)

    portlet_title = u''
    stories = None
    item_display = [u'image', u'description']
    more_text = u''
    extra_css = u''
    extra_id = u''
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', stories=None,
            item_display=[u'image', u'description'], more_text=u'', extra_css=u'', extra_id=u'', custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.stories = stories
        self.custom_header = custom_header
        self.omit_header = omit_header
        self.item_display = item_display
        self.more_text = more_text
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        msg = __(u"Stories portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('storiesportlet.pt')

    @instance.memoizedproperty
    def stories(self):
        if not self.data.stories:
            return None

        portal_path = getToolByName(self.context, 'portal_url').getPortalPath()
        item = self.context.restrictedTraverse(
            str(portal_path + self.data.stories),
            None
        )

        return item

    @instance.memoizedproperty
    def substories(self):
        items = []
        folders = list(self.stories.getFolderContents({'portal_type': 'ATSuccessStoryFolder'}, full_objects=True))
        for folder in folders:
            item = {}

            item['Title'] = folder.Title()
            stories = list(folder.getFolderContents({'portal_type': 'ATSuccessStory'}, full_objects=True))
            item['stories'] = stories[-1:]

            items.append(item)
        return items

    def header(self):
        return self.data.custom_header or self.stories.Title()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IStoriesPortlet)
    form_fields['stories'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IStoriesPortlet)
    form_fields['stories'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget
