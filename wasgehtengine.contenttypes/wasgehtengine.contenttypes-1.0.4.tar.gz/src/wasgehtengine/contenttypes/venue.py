# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from geoposition import IGeoPosition
from osmelement import IOsmElement
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer.decorator import indexer
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form import button, validator
from z3c.relationfield.schema import RelationList, RelationChoice, RelationList, \
    RelationChoice
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Invalid
from plone.memoize import ram
from datetime import datetime, timedelta

def get_venue_type(venue):
    if venue.osmReference is None:
        return None
        
    if venue.osmReference.osmElementTags is None:
        return None
        
    tags = venue.osmReference.osmElementTags
        
    if 'tourism' in tags and tags['tourism'] == 'museum':
        return 'museum'
    
    if 'shop' in tags and tags['shop'] == 'kiosk':
        return 'kiosk'
    
    if 'amenity' in tags:
        return tags['amenity']
        
    return None

class IVenue(form.Schema):
    """A venue
    """

    website = schema.URI(
                title=_("Website"),
                description=_("Venue's website"),
                required=False,
            )

    #form.omitted('geographicPosition')
    geographicPosition = schema.Object(
                title=_("Geographic Position"),
                description=_("Geographic coordinates of the venue"),
                schema=IGeoPosition,
                required=False,
            )

    postalAddress = schema.Text(
                title=_("Postal Address"),
                description=_("Postal Address of the venue"),
                required=False,
            )

    osmReference = schema.Object(
                title=_("OSM Reference"),
                description=_("Reference to the corresponding element in OpenStreetMap"),
                schema=IOsmElement,
                required=False,
                )
    
    phoneNumber = schema.ASCII(
                title=_("Phone Number"),
                description=_("Phone number"),
                required=False,
                )

class View(grok.View):
    """Default view (called "@@view"") for a venue.

    The associated template is found in venue_templates/view.pt.
    """

    grok.context(IVenue)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass
    
    def upcoming_events(self):
        return self.events_after((datetime.today() - timedelta(days=1)).date(), venue='/'.join(self.context.getPhysicalPath()))
        
    # cache this function until change    
    #@ram.cache(lambda method, self, start, venue: (start, venue))
    def events_after(self, start, venue):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults(portal_type='wasgehtengine.Event', period_start={ "query": [start, ], "range": "min" }, venue=venue)
        
        return sorted([brain.getObject() for brain in results], key=lambda event: event.period.start)
    
class VenueForm(form.SchemaForm):
    """ Define Form handling

    """
    grok.name('edit')
    grok.require('zope2.View')
    grok.context(IVenue)

    schema = IVenue

    #label = u"What's your name?"
    #description = u"Simple, sample form"
             

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            print(errors)
            print()
            print(data)
            return

        # Do something with valid data here

        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)
        self.status = "Thank you very much!"

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
