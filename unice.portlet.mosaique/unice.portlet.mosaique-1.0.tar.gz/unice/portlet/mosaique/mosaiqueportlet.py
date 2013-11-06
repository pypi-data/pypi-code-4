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

from unice.portlet.mosaique import MosaiquePortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

from Acquisition import aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm

from zope.component import getMultiAdapter

import re
import unicodedata

class IMosaiquePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(
        title=_(u'Titre du portlet dans le manager'),
        description=_('help_portlet_title',
                      default=u'Titre affiché dans l\'ecran "@@manage-portlets". '
                               'Laisser vide pour "Mosaique portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Titre du portlet"),
        description=_('help_custom_header',
                      default=u"Laisser vide pour afficher le titre le l'élément sélectionné"),
        required=False,
    )

    mosaique = schema.Choice(title=_(u"Elément à afficher"),
        required=True,
        source=SearchableTextSourceBinder(
            {},
            default_query='path:'
        )
    )

    columns = schema.TextLine(
        title=_(u'Nombre de colonnes à afficher'),
        description=_('help_columns',
                      default=u""),
        default=u'2',
        required=True,
    )

    item_display = schema.List(
        title=_(u'Options de la mosaique'),
        description=_('help_item_display',
                      default=u"Sélectionner les options à afficher"),
        value_type=schema.Choice(
            vocabulary='unice.portlet.mosaique.item_display_vocabulary',
        ),
        default=[u'title', u'desc', u'date', u'location'],
        required=False,
    )

    prefix_theme = schema.TextLine(
        title=_(u'Préfix des mots clés pour la classification par thème'),
        description=_('help_prefix_theme',
                      default=u""),
        default=u'',
        required=False,
    )
    prefix_importance = schema.TextLine(
        title=_(u'Préfix des mots clés pour la classification par importance'),
        description=_('help_prefix_importance',
                      default=u""),
        default=u'',
        required=False,
    )

    max_items = schema.TextLine(
        title=_(u'Nombre d\'éléments à afficher'),
        description=_('help_max_items',
                      default=u"Laisser vide pour afficher tous les éléments"),
        default=u'',
        required=False,
    )

    reduce_height = schema.TextLine(
        title=_(u'Réduction de la hauteur des images'),
        description=_('help_reduce_height',
                      default=u"Réduire la hauteur des images (en pixels)"),
        default=u'0',
        required=True,
    )

    more_text = schema.TextLine(
        title=_(u'Texte du bouton "Afficher plus d\'élément'),
        description=_('help_more_text',
                      default=u""),
        default=u'Afficher plus d\'élements',
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

    implements(IMosaiquePortlet)

    portlet_title = u''
    mosaique = None
    columns = u''
    item_display = [u'image', u'description']
    prefix_theme = u''
    prefix_importance = u''
    max_items = u''
    reduce_height = u''
    more_text = u''
    extra_css = u''
    extra_id = u''
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', mosaique=None, columns=u'', item_display=[u'image', u'description'], prefix_theme=u'', prefix_importance=u'', max_items=u'', reduce_height=u'', more_text=u'', extra_css=u'', extra_id=u'', custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.mosaique = mosaique
        self.custom_header = custom_header
        self.omit_header = omit_header
        self.columns = columns
        self.item_display = item_display
        self.prefix_theme = prefix_theme
        self.prefix_importance = prefix_importance
        self.max_items = max_items
        self.reduce_height = reduce_height
        self.more_text = more_text
        self.extra_css = extra_css
        self.extra_id = extra_id

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        msg = __(u"Mosaique portlet")
        return self.portlet_title or msg


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('mosaiqueportlet.pt')

    @instance.memoizedproperty
    def mosaique(self):
        if not self.data.mosaique:
            return None

        portal_path = getToolByName(self.context, 'portal_url').getPortalPath()
        item = self.context.restrictedTraverse(
            str(portal_path + self.data.mosaique),
            None
        )

        return item

    @instance.memoizedproperty
    def submosaique(self):
        items = []
        objs = []

        if self.mosaique.portal_type == 'Collection':
            objs = [obj.getObject() for obj in self.mosaique.queryCatalog()]
        else:
            objs = self.mosaique.objectValues()

        for obj in objs:
            image = None
            if hasattr(obj, 'tag'):
                image = obj.tag(scale='large', css_class='')
            leadimage = self.contentLeadImage(obj)
            if leadimage:
                image = leadimage

            if image:
                src = re.findall(r'src\s*=\s*["\']([^"\']*)["\']', image)
                image = src[0] if len(src)>0 else None

            if not image:
                image = 'holder.js/768x576/auto/text:%s' % self.header()

            print '================================================================'
            print obj.Title()
            print obj.Subject()
            print self.data.prefix_theme
            
            items.append({
                'obj': obj,
                'type': obj.portal_type,
                'image': image,
                'date': self.eventDate(obj),
                'location': self.eventLocation(obj),
                'theme': self.filtrerSubjects(obj.Subject(), self.data.prefix_theme),
                'importance': self.filtrerSubjects(obj.Subject(), self.data.prefix_importance),
            })

        return items

    def header(self):
        return self.data.custom_header or self.mosaique.Title()

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

    def captions(self, item):
        captions = []
        if 'title' in self.data.item_display:
            captions.append('<h3>%s</h3>' % item['obj'].Title())
        if 'date' in self.data.item_display and item['date']:
            captions.append(' <i class="icon-calendar-empty"></i> <small>%s</small>' % item['date'])
        if 'location' in self.data.item_display and item['location']:
            captions.append(' - <i class="icon-map-marker"></i> <small>%s</small>' % item['location'])
        if 'desc' in self.data.item_display:
            captions.append('<p><small>%s</small></p>' % self.smart_truncate(item['obj'].Description()))
        return ''.join(captions)

    def reduce_css(self):
        h = int(self.data.reduce_height)/2
        return 'margin-top:-%spx; margin-bottom:-%spx;' % (h, h)

    def smart_truncate(self, content, length=200, suffix='...'):
        if len(content) <= length:
            return content
        else:
            return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

    def cols(self, index):
        if not self.data.max_items:
            return int(self.data.columns)
        else:
            return int(self.data.columns) if index < int(self.data.max_items) else 1

    def filtrerSubjects(self, subjects, prefix):
        filtered = [self.cleanSubject(s, prefix) for s in subjects if s.decode('utf-8').startswith(prefix)] if prefix else None
        return None if not filtered or len(filtered) == 0 else filtered[0]

    def cleanSubject(self, subject, prefix):
        suffix = self.strip_accents(subject[len(prefix):])
        suffix_id = re.sub('[\s\-,;\|\(\)]+', '-', suffix.lower().strip())
        suffix_id = int(suffix_id) if suffix_id.isdigit() else suffix_id
        return {'subject':subject, 'suffix':suffix, 'suffix_id':suffix_id}

    def strip_accents(self, s):
        s = s.decode('utf-8')
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMosaiquePortlet)
    form_fields['mosaique'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMosaiquePortlet)
    form_fields['mosaique'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget
