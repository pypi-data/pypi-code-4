__version__ = '$Id$'

from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.memoize.instance import memoize
from plone.memoize.compress import xhtml_compress

from plone.app.portlets.portlets import base
from plone.app.portlets.portlets.navigation import INavigationPortlet
from plone.app.portlets.portlets.navigation import Assignment as BaseAssignment
from plone.app.portlets.portlets.navigation import Renderer as BaseRenderer
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from cs.navigation import messagefactory as _

class ICSNavigationPortlet(INavigationPortlet):
    show_icons = schema.Bool(
        title=_(u'label_show_icons',
                default=u'Show content-type icons'),
        description=_(u'help_show_icons',
                      default=u'Whether or not to show the icons of '
                               'the content-types shown in the '
                               'navigation tree'),
        default=True,
        required=False)
                

class Assignment(BaseAssignment):
    implements(ICSNavigationPortlet)
    
    show_icons = 1

    def __init__(self, name=u'', root=None, currentFolderOnly=False, includeTop=False, topLevel=1, bottomLevel=0, show_icons=0):
        super(Assignment, self).__init__(name, root, currentFolderOnly, includeTop, topLevel, bottomLevel)
        self.show_icons = show_icons

        
class Renderer(BaseRenderer):

    def title(self):
        return self.data.name or u''

    @memoize
    def show_icons(self):
        return self.data.show_icons

    _template = ViewPageTemplateFile('navigation.pt')
    recurse = ViewPageTemplateFile('navigation_recurse.pt')

class AddForm(base.AddForm):
    form_fields = form.Fields(ICSNavigationPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u"Add Navigation Portlet")
    description = _(u"This portlet display a navigation tree.")

    def create(self, data):
        return Assignment(name=data.get('name', u""),
                          root=data.get('root', u""),
                          currentFolderOnly=data.get('currentFolderOnly', False),
                          topLevel=data.get('topLevel', 0),
                          bottomLevel=data.get('bottomLevel', 0),
                          show_icons=data.get('show_icons', 1))


class EditForm(base.EditForm):
    form_fields = form.Fields(ICSNavigationPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u"Edit Navigation Portlet")
    description = _(u"This portlet displays a navigation tree.")

