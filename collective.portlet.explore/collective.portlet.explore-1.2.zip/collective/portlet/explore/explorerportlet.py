from zope.interface import implements
from plone.app.portlets.portlets import navigation as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.portlet.explore import ExplorerPortletMessageFactory as _

class IExplorerPortlet(base.INavigationPortlet):
    """A portlet
    """

class Assignment(base.Assignment):
    """Portlet assignment.
    """
    implements(IExplorerPortlet)

    title = _(u"Explorer Portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    recurse = ViewPageTemplateFile('recurse.pt')


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    label = _(u"Add Explorer Portlet")
    description = _(u"This portlet display a collapsible navigation tree.")

    def create(self, data):
        return Assignment(name=data.get('name', u""),
                          root=data.get('root', u""),
                          currentFolderOnly=data.get('currentFolderOnly', False),
                          topLevel=data.get('topLevel', 0),
                          bottomLevel=data.get('bottomLevel', 0))


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    label = _(u"Edit Explorer Portlet")
    description = _(u"This portlet display a collapsible navigation tree.")

