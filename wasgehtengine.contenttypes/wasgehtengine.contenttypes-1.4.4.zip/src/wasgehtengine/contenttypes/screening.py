# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer import indexer
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
from venue import IVenue
from movie import IMovie
from event import IEvent
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form import validator
from z3c.relationfield.schema import RelationList, RelationChoice, RelationList, \
    RelationChoice, Relation
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Invalid
from DateTime import DateTime

class IScreening(IEvent):
    """A screening of a movie
    """
    
    #movie = RelationChoice(
    #            title=_("Movie"),
    #            description=_("The movie presented in this screening"),
    #            source=ObjPathSourceBinder(object_provides=IMovie.__identifier__),
    #            required=True,
    #        )
    
    movie_title = schema.TextLine(
                    title = _("Movie title"),
                    description=_("The movie presented in this screening"),
                    required=True,
                )

class View(grok.View):
    """Default view (called "@@view"") for a screening.

    The associated template is found in screening_templates/view.pt.
    """

    grok.context(IScreening)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass
    
    def autoimport_url(self):
        
        event_import_status = self.get_event_import_status()
        
        if event_import_status is not None:
            return event_import_status.absolute_url()
    
    def get_event_import_status(self): 
        catalog = getToolByName(self.context, 'portal_catalog')
        
        results = catalog.searchResults(portal_type='wasgehtengine.EventImportStatus', venue='/'.join(self.context.venue.to_object.getPhysicalPath()))
        
        if results == None or len(results) == 0:
            return None
        
        return results[0].getObject()