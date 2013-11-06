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

from unice.portlet.telechargement import TelechargementPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

class ITelechargementPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Telechargement portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )

    telechargement = schema.Choice(title=_(u"Elément à afficher"),
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
    implements(ITelechargementPortlet)

    portlet_title = u''
    telechargement = None
    extra_css = u''
    extra_id = u''
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', telechargement=None, extra_css=u'', extra_id=u'', custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.telechargement = telechargement
        self.custom_header = custom_header
        self.omit_header = omit_header
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        msg = __(u"Telechargement portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('telechargementportlet.pt')

    @instance.memoizedproperty
    def telechargement(self):
        if not self.data.telechargement:
            return None

        portal_path = getToolByName(self.context, 'portal_url').getPortalPath()
        item = self.context.restrictedTraverse(
            str(portal_path + self.data.telechargement),
            None
        )

        return item

    @instance.memoizedproperty
    def subtelechargement(self):
        items = []
        folders = list(self.telechargement.getFolderContents({'portal_type': 'ATSuccessStoryFolder'}, full_objects=True))
        for folder in folders:
            item = {}

            item['Title'] = folder.Title()
            telechargement = list(folder.getFolderContents({'portal_type': 'ATSuccessStory'}, full_objects=True))
            item['telechargement'] = telechargement[-1:]

            items.append(item)
        return items

    def header(self):
        return self.data.custom_header or self.telechargement.Title()


class AddForm(base.AddForm):
    form_fields = form.Fields(ITelechargementPortlet)
    form_fields['telechargement'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ITelechargementPortlet)
    form_fields['telechargement'].custom_widget = UberSelectionWidget
