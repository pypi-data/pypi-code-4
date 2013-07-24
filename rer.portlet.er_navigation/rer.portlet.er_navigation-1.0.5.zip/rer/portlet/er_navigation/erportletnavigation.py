from zope.interface import implements
from zope import schema
from plone.app.portlets.portlets import navigation
from plone.app.portlets.portlets import base
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.portlet.er_navigation import ERPortletNavigationMessageFactory as _
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

class IERPortletNavigation(navigation.INavigationPortlet):
    """A portlet that inherit from base navigation
    """
   
    topLevel = schema.Int(
            title=_(u"label_navigation_startlevel", default=u"Start level"),
            description=_(u"help_navigation_start_level",
                default=u"An integer value that specifies the number of folder "
                         "levels below the site root that must be exceeded "
                         "before the navigation tree will display. 0 means "
                         "that the navigation tree should be displayed "
                         "everywhere including pages in the root of the site. "
                         "1 means the tree only shows up inside folders "
                         "located in the root and downwards, never showing "
                         "at the top level."),
            default=0,
            required=False)
    
    portlet_class = schema.TextLine(title=_(u"Portlet class"),
                                    required=False,
                                    description=_(u"Css class to add at the portlet"))

class Assignment(navigation.Assignment):
    """Portlet assignment.
    """

    implements(IERPortletNavigation)

    portlet_class= ''
        
    def __init__(self, name=u"", root=None, currentFolderOnly=False,
                 includeTop=False, topLevel=0, bottomLevel=0,portlet_class= ''):
        super(Assignment, self).__init__(name = name,
                                         root = root,
                                         currentFolderOnly = currentFolderOnly,
                                         includeTop = includeTop,
                                         topLevel = topLevel,
                                         bottomLevel = bottomLevel)
        
        self.portlet_class= portlet_class

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        if self.name:
            return "ER navigation: %s" %self.name 
        return _(u"ER navigation: no title")


class Renderer(navigation.Renderer):
    """Portlet renderer.
    """

    _template = ViewPageTemplateFile('erportletnavigation.pt')
    recurse = ViewPageTemplateFile('er_navigation_recurse.pt')

class AddForm(navigation.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(IERPortletNavigation)
    form_fields['root'].custom_widget = UberSelectionWidget
    
    def create(self, data):
        return Assignment(name=data.get('name', u""),
                          root=data.get('root', u""),
                          currentFolderOnly=data.get('currentFolderOnly', False),
                          includeTop=data.get('includeTop', False),
                          topLevel=data.get('topLevel', 0),
                          bottomLevel=data.get('bottomLevel', 0),
                          portlet_class=data.get('portlet_class', u""))


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(IERPortletNavigation)
    form_fields['root'].custom_widget = UberSelectionWidget