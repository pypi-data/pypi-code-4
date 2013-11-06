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

from unice.portlet.vimeo import VimeoPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

class IVimeoPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Vimeo portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )

    video_id = schema.TextLine(
        title=_(u"Identifiant de la vidéo"),
        description=_('help_video_id',
                      default=u"Identifiant dans l'adresse de la vidéo http://vimeo.com/XXXXXXX"),
        required=True,
    )
    video_width = schema.TextLine(
        title=_(u"Largeur de la vidéo"),
        description=_('help_video_width',
                      default=u"En pourcentage ou en pixels"),
        default=u'100%',
        required=True,
    )
    video_height = schema.TextLine(
        title=_(u"Hauteur de la vidéo"),
        description=_('help_video_height',
                      default=u"En pixels"),
        default=u'320px',
        required=True,
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
    implements(IVimeoPortlet)

    portlet_title = u''
    extra_css = u''
    extra_id = u''
    custom_header = u""
    video_id = u""
    video_width = u""
    video_height = u""
    omit_header = False

    def __init__(self, portlet_title=u'',  extra_css=u'', extra_id=u'', custom_header=None, video_id=u'', video_width=u'', video_height=u'', omit_header=None):
        self.portlet_title = portlet_title
        self.custom_header = custom_header
        self.video_id = video_id
        self.video_width = video_width
        self.video_height = video_height
        self.omit_header = omit_header
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        msg = __(u"Vimeo portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('vimeoportlet.pt')

    def header(self):
        return self.data.custom_header


class AddForm(base.AddForm):
    form_fields = form.Fields(IVimeoPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IVimeoPortlet)
