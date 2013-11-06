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

from unice.portlet.flickr import FlickrPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

import re

class IFlickrPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Flickr portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )

    user_id = schema.TextLine(
        title=_(u"Identifiant du compte Flickr"),
        description=_('help_user_id',
                      default=u"Voir sur http://idgettr.com/"),
        required=True,
    )
    albums = schema.TextLine(
        title=_(u"Identifiants des albums"),
        description=_('help_albums',
                      default=u"Identifiants séparés par des virgules"),
        required=True,
    )
    nbr_photos = schema.TextLine(
        title=_(u"Nombre de photos"),
        description=_('help_nbr_photos',
                      default=u"Nombre de photos à afficher par album"),
        default=u'100%',
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
    implements(IFlickrPortlet)

    portlet_title = u''
    extra_css = u''
    extra_id = u''
    custom_header = u""
    user_id = u""
    albums = u""
    nbr_photos = u""
    omit_header = False

    def __init__(self, portlet_title=u'',  extra_css=u'', extra_id=u'', custom_header=None, user_id=u'', albums=u'', nbr_photos=u'', omit_header=None):
        self.portlet_title = portlet_title
        self.custom_header = custom_header
        self.user_id = user_id
        self.albums = albums
        self.nbr_photos = nbr_photos
        self.omit_header = omit_header
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        msg = __(u"Flickr portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('flickrportlet.pt')

    def header(self):
        return self.data.custom_header

    def albums(self):
        return re.split("[ ,;]+", self.data.albums)


class AddForm(base.AddForm):
    form_fields = form.Fields(IFlickrPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IFlickrPortlet)
