################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

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
from ..interfaces import IInstitution, IBase


class IDepartmentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

class DepartmentPortletAssignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IDepartmentPortlet,IBase)

    department_uid = ''

    def __init__(self, department_uid=''):
        self.department_uid = department_uid

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u'label_departmentportlet')


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('departmentportlet.pt')

    _template = ViewPageTemplateFile('departmentportlet.pt')

    # @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self._data()) > 0
        # return self._data() is not None
        #return 1

    def getDepartment(self):
        return self._data()

    @memoize
    def _data(self):
        department=None
        instdic=None
        context = aq_inner(self.context)
        #ref_catalog = getToolByName(context, 'reference_catalog')
        catalog = getToolByName(context, 'portal_catalog')
        uid = self.data.department_uid
        if uid:
             result = list(catalog(UID=uid,))
             if len(result):
                department = result[0].getObject()
        depdic={}
        if department:
            staff_view = StaffSortView(department, None)
            image_view = ImageView(department, None)
            
            depdic={
                'title':    department.Title(),
                'buildingsection':    department.getBuildingsection(),
                'addresses':      department.getAddresses(),
                'email':    department.getEmail(),
                'email_to_show': department.getEmail() and department.getEmail().replace('@', ' @ ') or '', 
                'homepage': department.getUrl(),
                'url':      department.absolute_url(),
                'staff':    staff_view.getSortedStaff(),
                'image': image_view.getReferenceImage(),
            }
        return depdic

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IDepartmentPortlet)

    def create(self, data):
        return DepartmentPortletAssignment(department_uid=self.context.UID())


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IDepartmentPortlet)
