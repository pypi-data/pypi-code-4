from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.unslider import MessageFactory as _
from plone.app.portlets.browser import z3cformhelper
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationList, RelationChoice
from collective.sliderfields.interfaces import ISliderFieldsEnabled
from z3c.form import field
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget

from zope.component import getMultiAdapter, getUtility
from AccessControl import getSecurityManager


class IUnsliderPortlet(IPortletDataProvider):
    """
    Define your portlet schema here
    """
    width = schema.Int(title=_(u'Width'), default=1024)
    height = schema.Int(title=_(u'Height'), default=350)

    contents = schema.List(
        title=_(u'Contents'),
        value_type=schema.Choice(
            source=SearchableTextSourceBinder({
                'object_provides': ISliderFieldsEnabled.__identifier__
            }, 
            default_query='path:')
        )
    )

class Assignment(base.Assignment):
    implements(IUnsliderPortlet)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def title(self):
        return _('Unslider Portlet')

class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('templates/unsliderportlet.pt')

    @property
    def available(self):
        return True

    def _get_object(self, path):
        if not path:
            return None

        if path.startswith('/'):
            path = path[1:]

        if not path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(path, unicode):
            # restrictedTraverse accepts only strings
            path = str(path)

        result = portal.unrestrictedTraverse(path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
        return result


    def contents(self):
        data = []
        for i in self.data.contents:
            obj = self._get_object(i)
            if obj is None:
                continue
            title = getattr(obj, 'slider_title', None)
            if not title:
                title = obj.Title()
            description = getattr(obj, 'slider_description', None)
            if not description:
                description = obj.Description()

            scales = obj.restrictedTraverse('@@images')
            image = scales.scale('slider_image', width=self.data.width,
                                    height=self.data.height)

            if image:
                image_url = image.url
            else:
                image_url = 'http://placehold.it/%sx%s' % (height, width)
            
            data.append({
                'title': title,
                'description': description,
                'image_url': image_url,
                'url': obj.absolute_url(),
                'slide_css': 
                    """
                        height: %spx;
                        width: %spx;
                        background-image:url('%s');
                    """ % (
                        self.data.height, self.data.width, image_url
                    )
            })
        return data

    def style(self):
        return 'height:%spx;width:%spx;' % (self.data.height, self.data.width)


class AddForm(base.AddForm):
    form_fields = form.Fields(IUnsliderPortlet)
    form_fields['contents'].custom_widget = UberMultiSelectionWidget
    label = _(u"Add Unslider Portlet")
    description = _(u"")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IUnsliderPortlet)
    form_fields['contents'].custom_widget = UberMultiSelectionWidget
    label = _(u"Edit Unslider Portlet")
    description = _(u"")
