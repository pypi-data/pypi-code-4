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

from unice.portlet.coordonnees import CoordonneesPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

import re

class ICoordonneesPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Coordonnees portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )


    entete = schema.TextLine(
        title=_(u"Entête"),
        description=_('help_entete',
                      default=u""),
        required=False,
    )

    nom = schema.TextLine(
        title=_(u"Nom du service ou de la composante"),
        description=_('help_nom',
                      default=u""),
        required=False,
    )
    adresse = schema.TextLine(
        title=_(u"Adresse postale"),
        description=_('help_adresse',
                      default=u""),
        required=False,
    )
    code_postal = schema.TextLine(
        title=_(u"Code postal"),
        description=_('help_code_postal',
                      default=u""),
        required=False,
    )
    ville = schema.TextLine(
        title=_(u"Ville"),
        description=_('help_ville',
                      default=u""),
        required=False,
    )

    telephone = schema.TextLine(
        title=_(u"Téléphone"),
        description=_('help_telephone',
                      default=u""),
        required=False,
    )

    fax = schema.TextLine(
        title=_(u"Fax"),
        description=_('help_fax',
                      default=u""),
        required=False,
    )

    email = schema.TextLine(
        title=_(u"Email"),
        description=_('help_email',
                      default=u""),
        required=False,
    )

    pied_page = schema.TextLine(
        title=_(u"Pied de page"),
        description=_('help_pied_page',
                      default=u""),
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
    implements(ICoordonneesPortlet)

    portlet_title = u''
    extra_css = u''
    extra_id = u''
    custom_header = u""
    entete = u""
    nom = u""
    adresse = u""
    code_postal = u""
    ville = u""
    telephone = u""
    fax = u""
    email = u""
    pied_page = u""
    omit_header = False

    def __init__(self, portlet_title=u'',  extra_css=u'', extra_id=u'', custom_header=None, entete=u'', nom=u'', adresse=u'', code_postal=u'', ville=u'', telephone=u'', fax=u'', email=u'', pied_page=u'', omit_header=None):
        self.portlet_title = portlet_title
        self.custom_header = custom_header
        self.entete = entete
        self.nom = nom
        self.adresse = adresse
        self.code_postal = code_postal
        self.ville = ville
        self.telephone = telephone
        self.fax = fax
        self.email = email
        self.pied_page = pied_page
        self.omit_header = omit_header
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        msg = __(u"Coordonnees portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('coordonneesportlet.pt')

    def header(self):
        return self.data.custom_header


class AddForm(base.AddForm):
    form_fields = form.Fields(ICoordonneesPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ICoordonneesPortlet)
