################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: institutionportlet.py 2981 2011-03-16 10:54:12Z carsten $

from zope import schema
from zope.formlib import form
from zope.interface import Interface
from zope.interface import implements
from zope.i18nmessageid import MessageFactory

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from .. import orgMessageFactory as _
from ..browser.imagesupport import ImageView
from ..browser.staffsort import StaffSortView
from ..browser.vbbsupport import VBBView
from ..interfaces import IInstitution, IBase


class IInstitutionPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    institution_uid = schema.Choice(
        vocabulary = u'source_institutions',
        title    = _(u'box_label_institution'),
        required = True,
    )

class InstitutionPortletAssignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IInstitutionPortlet,IBase)

    institution_uid = ''

    def __init__(self, institution_uid=''):
        self.institution_uid = institution_uid

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u'box_label_institutionportlet') 


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('institutionportlet.pt')

    _template = ViewPageTemplateFile('institutionportlet.pt')

    # @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        # return self._data() is not None
        return 1

    def getInstitution(self):
        return self._data()

    @memoize
    def _data(self):
        institution=None
        instdic=None
        context = aq_inner(self.context)
        ref_catalog = getToolByName(context, 'reference_catalog')
        uid = self.data.institution_uid
        institution = ref_catalog.lookupObject(uid)
        instdic={}
        if institution:
            vbb_view = VBBView(institution, None)
            staff_view = StaffSortView(institution, None)
            image_view = ImageView(institution, None)
            instdic={
                'title': institution.Title(),
                'addresses': institution.getAddresses(),
#                'state': institution.state(),
                'email': institution.getEmail(),
                'email_to_show': institution.getEmail().replace('@', ' @ '),
                'homepage': institution.getUrl(),
                'url': institution.absolute_url(),
                'vbb': vbb_view.getVBBUrl(),
                'staff': staff_view.getSortedStaff(),
                'image': image_view.getReferenceImage(),
                'institution': institution,
            }
        return instdic


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IInstitutionPortlet)

    def create(self):
        return InstitutionPortletAssignment(institution_uid=self.context.UID())

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IInstitutionPortlet)
