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

from unice.portlet.boutique import BoutiquePortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

from prestashop import Prestashop

class IBoutiquePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Boutique portlet".'),
        required=True,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre du portlet du manager"),
        required=False,
    )

    serveur = schema.TextLine(
        title=_(u'Adresse du serveur de la boutique'),
        description=_('help_serveur',
                      default=u""),
        default=u'',
        required=True,
    )
    dossier = schema.TextLine(
        title=_(u'Dossier de la boutique sur le serveur'),
        description=_('help_dossier',
                      default=u""),
        default=u'',
        required=True,
    )
    cle = schema.TextLine(
        title=_(u"Clé d'authentification aux webservices"),
        description=_('help_cle',
                      default=u""),
        default=u'',
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
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBoutiquePortlet)

    portlet_title = u''
    serveur = u''
    dossier = u''
    cle = u''
    extra_css = u''
    extra_id = u''
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', serveur=u'', dossier=u'', cle=u'', extra_css=u'', extra_id=u'', custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.custom_header = custom_header
        self.omit_header = omit_header
        self.serveur = serveur
        self.dossier = dossier
        self.cle = cle
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        msg = __(u"Boutique portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('boutiqueportlet.pt')

    def header(self):
        return self.data.custom_header or self.data.portlet_title

    def produits(self):
        #serveur = 'http://boutique-uns.com'
        #dossier = 'uns'
        #cle = '8MMGXQX2WCG10DU7KAXZ1LCHPAFV9YO6'

        prestashop = Prestashop(self.data.serveur, self.data.dossier, self.data.cle)
        return prestashop.produits()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IBoutiquePortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IBoutiquePortlet)
