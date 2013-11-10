from five import grok
from zope import schema
from plone.directives import form

from plone.app.textfield import RichText

from wasgehtengine.contenttypes.venue import IVenue
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser

from zope.lifecycleevent.interfaces import IObjectAddedEvent

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Acquisition import aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager
from venue import get_venue_type

class IBlogFolder(form.Schema):
    """A folder that can contain blog posts 
    """
    pass

class View(grok.View):
    """Default view (called "@@view"") for a blog folder.
    
    The associated template is found in blogfolder_templates/view.pt.
    """
    
    grok.context(IBlogFolder)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        pass
    
    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')
        
    def authorname(self, authorid):
        membership = getToolByName(self.context, 'portal_membership')
        author = membership.getMemberInfo(authorid)
        return author and author['fullname'] or authorid