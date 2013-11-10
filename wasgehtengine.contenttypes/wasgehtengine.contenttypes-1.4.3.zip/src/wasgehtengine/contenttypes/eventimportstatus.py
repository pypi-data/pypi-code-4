# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer.decorator import indexer
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
from venue import IVenue
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form import button, validator, converter, interfaces
from z3c.relationfield.schema import RelationList, RelationChoice, RelationList, \
    RelationChoice
from zope import schema
from zope.component import getMultiAdapter, adapts
from zope.interface import Invalid, implements
from plone.memoize import ram
from datetime import datetime, timedelta
from zope.i18n import format

class IEventImportStatus(form.Schema):
    """Event import status for a venue
    """
    
    venue = RelationChoice(
                title=_("Venue"),
                description=_("Venue for which events are imported"),
                source=ObjPathSourceBinder(object_provides=IVenue.__identifier__),
                required=True,
            )
    
    last_run = schema.Datetime(
                title=_("Last run"),    
                required=False,
            )

    last_successful_run = schema.Datetime(
                title=_("Last successful run"),    
                required=False,
            )
    
    last_run_with_events_imported = schema.Datetime(
                title=_("Last successful run which imported events"),    
                required=False,
            )
    
    imported_events_count = schema.Int(
                title=_("Imported/updated events"),
                description=_("Number of events imported at last successful run"),
                required=False,
            )
    
class View(grok.View):
    """Default view (called "@@view"") for an event import status item.

    The associated template is found in eventimportstatus_templates/view.pt.
    """

    grok.context(IEventImportStatus)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass
    
@indexer(IEventImportStatus)
def venue_indexer(context):    
    return str('/'.join(context.venue.to_object.getPhysicalPath()))

grok.global_adapter(venue_indexer, name="venue")