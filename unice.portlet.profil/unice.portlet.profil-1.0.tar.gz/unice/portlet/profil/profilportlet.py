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

from unice.portlet.profil import ProfilPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

from Acquisition import aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm

class IProfilPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Profil portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )

    profil = schema.Choice(title=_(u"Elément à afficher"),
        required=True,
        source=SearchableTextSourceBinder(
            {},
            default_query='path:'
        )
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
    implements(IProfilPortlet)

    portlet_title = u''
    profil = None
    extra_css = u''
    extra_id = u''
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', profil=None, extra_css=u'', extra_id=u'', custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.profil = profil
        self.custom_header = custom_header
        self.omit_header = omit_header
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        msg = __(u"Profil portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('profilportlet.pt')

    @instance.memoizedproperty
    def profil(self):
        if not self.data.profil:
            return None

        portal_path = getToolByName(self.context, 'portal_url').getPortalPath()
        item = self.context.restrictedTraverse(
            str(portal_path + self.data.profil),
            None
        )

        return item

    def header(self):
        return self.data.custom_header or self.profil.Title()



    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def contentLeadImage(self, css_class=''):
        context = aq_inner(self.profil)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)
        if titlef is not None:
            title = titlef.get(context)
        else:
            title = ''
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.body_scale_name
                return field.tag(context, scale=scale, css_class=css_class, title=title)
        return ''



class AddForm(base.AddForm):
    form_fields = form.Fields(IProfilPortlet)
    form_fields['profil'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IProfilPortlet)
    form_fields['profil'].custom_widget = UberSelectionWidget
