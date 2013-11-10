from five import grok
from zope import schema
from plone.directives import form

from wasgehtengine.contenttypes.eventimportstatus import IEventImportStatus
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser

from zope.lifecycleevent.interfaces import IObjectAddedEvent

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Acquisition import aq_parent

from DateTime import DateTime
from datetime import timedelta
from datetime import datetime
import iso8601
import locale

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager
from plone.memoize import ram

class IEventImportStatusFolder(form.Schema):
    """A folder that can contain eventimport status objects
    """
    pass

class View(grok.View):
    """Default view (called "@@view"") for a event folder.
    
    The associated template is found in eventfolder_templates/view.pt.
    """
    
    grok.context(IEventImportStatusFolder)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        pass
    
    
class IEventImportStatusFolderViewlet(BrowserView):
    implements(IViewlet)
    
    render = ViewPageTemplateFile('eventimportstatusfolder_templates/eventimportstatusfolder_viewlet.pt')

    def update(self):
       pass
   
    def children(self):
        """Get all status items in this folder
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        results = catalog({'object_provides': IEventImportStatus.__identifier__,
                             'path': dict(query='/'.join(self.context.getPhysicalPath()),
                                      depth=1),
                             'sort_on': 'sortable_title'})
        
        children = []
        
        for brain in results:            
            children.append(brain.getObject())
                
        return children

class IEventImportStatusFolderViewletManager(IViewletManager):
    """A viewlet manager...
    """