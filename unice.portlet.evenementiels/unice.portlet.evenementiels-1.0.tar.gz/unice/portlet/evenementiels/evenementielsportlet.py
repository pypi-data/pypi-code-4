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

from unice.portlet.evenementiels import EvenementielsPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

from Acquisition import aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm

from zope.component import getMultiAdapter

class IEvenementielsPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Evenementiels portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )

    evenementiels = schema.Choice(title=_(u"Elément à afficher"),
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
            vocabulary='unice.portlet.evenementiels.item_display_vocabulary',
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

    implements(IEvenementielsPortlet)

    portlet_title = u''
    evenementiels = None
    item_display = [u'image', u'description']
    more_text = u''
    extra_css = u''
    extra_id = u''
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', evenementiels=None,
            item_display=[u'image', u'description'], more_text=u'', extra_css=u'', extra_id=u'', custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.evenementiels = evenementiels
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
        msg = __(u"Evenementiels portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('evenementielsportlet.pt')

    @instance.memoizedproperty
    def evenementiels(self):
        if not self.data.evenementiels:
            return None

        portal_path = getToolByName(self.context, 'portal_url').getPortalPath()
        item = self.context.restrictedTraverse(
            str(portal_path + self.data.evenementiels),
            None
        )

        return item

    @instance.memoizedproperty
    def subevenementiels(self):
        items = []
        objs = []

        if self.evenementiels.portal_type == 'Collection':
            objs = [obj.getObject() for obj in self.evenementiels.queryCatalog({'portal_type': ['ATNewsItem', 'ATEvent', 'ATSuccessStory', 'ATFolder']})]
        else:
            objs = self.evenementiels.objectValues(['ATNewsItem', 'ATEvent', 'ATSuccessStory', 'ATFolder'])

        for obj in objs:
            image = None
            if hasattr(obj, 'tag'):
                image = obj.tag(scale='large', css_class='')
            leadimage = self.contentLeadImage(obj)
            if leadimage:
                image = leadimage

            items.append({'obj': obj, 'type': obj.portal_type, 'image': image, 'date': self.eventDate(obj), 'location': self.eventLocation(obj)})

        return items

    def header(self):
        return self.data.custom_header or self.evenementiels.Title()

    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def contentLeadImage(self, obj, css_class=''):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)
        if titlef is not None:
            title = titlef.get(context)
        else:
            title = ''
        if field is not None:
            if field.get_size(context) != 0:
                return field.tag(context, scale='large', css_class=css_class, title=title)
        return None


    def eventDate(self, item):
        if not item.portal_type == 'Event': return None

        plone = getMultiAdapter((self.context, self.request), name="plone")
        item_startdate = plone.toLocalizedTime(item.start())
        item_enddate = plone.toLocalizedTime(item.end())
        item_samedate = item.end() - item.start() < 1
        return item_startdate if item_samedate else '%s - %s' % (item_startdate, item_enddate)

    def eventLocation(self, item):
        if not item.portal_type == 'Event': return None

        return item.location if item.location else None

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IEvenementielsPortlet)
    form_fields['evenementiels'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IEvenementielsPortlet)
    form_fields['evenementiels'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget
