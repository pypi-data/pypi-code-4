import logging

from zope.interface import Interface
from zope.interface import implements
from zope.component import getMultiAdapter

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName

from collective.liches import lichesMessageFactory as _

from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

logger = logging.getLogger('collective.liches.portlet')


class ILichesPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    relative_path = schema.Bool(
        title=_(u"In this section"),
        description=_(u"""Display broken pages in this section only,
                        If unchecked all broken pages in the site will
                        be displayed"""),
        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ILichesPortlet)

    # Set default values for the configurable parameters here

    relative_path = False

    # Add keyword parameters for configurable parameters here
    def __init__(self, relative_path=False):
        self.relative_path = relative_path


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return __(u"Pages with broken links")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('lichesportlet.pt')

    @property
    def available(self):
        # Show this portlet for logged in users only
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        anonymous = portal_state.anonymous()
        return not anonymous


    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')()

    def get_js(self):
        template = """
        /*<![CDATA[*/
        $(document).ready(function() {
            var url =  '%s/@@liches-ajax-portlet.html';
            jQuery.get(url,
                function(data) {
                    $('#liches-portlet-container').html(data);
            });
        });/*]]>*/"""
        if self.data.relative_path:
            context = self.context.aq_inner
            url = context.absolute_url()
        else:
            url = self.portal_url
        return template % url



# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ILichesPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ILichesPortlet)
