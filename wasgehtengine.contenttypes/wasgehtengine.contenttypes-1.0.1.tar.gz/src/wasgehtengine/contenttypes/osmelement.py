# -*- coding: utf-8 -*-

from plone.directives import form
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form.interfaces import IObjectFactory
from zope import schema
from zope.component import adapts
from zope.interface import Interface, implements

class IOsmElement(Interface):
    """ An element in the OpenStreetMap database
    """

    osmElementId = schema.Int(
                title=_("OSM Element ID"),
                description=_("OSM Element ID"),
                required=True,
            )

    osmElementType = schema.Choice(
                title=_("OSM Element Type"),
                description=_("OSM Element Type"),
                required=True,
                values=["Node", "Way", "Relation"],
            )
    
    # There is no widget for schema.Dict so this raises a ComponentLookupError
    #osmElementTags = schema.Dict(
    #            title=_("OSM Element Tags"),
    #            description=_("OSM Element Tags"),
    #            required=False,
    #            key_type=schema.TextLine(title=_("Key")),
    #            value_type=schema.TextLine(title=_("Value")),
    #        )
    
class OsmElementFactory(object):
     adapts(Interface, Interface, Interface, Interface)
     implements(IObjectFactory)

     def __init__(self, context, request, form, widget):
         pass

     def __call__(self, value):
         return OsmElement(value)
     
class OsmElement(object):
     implements(IOsmElement)

     def __init__(self, value=None):
         if value:
             self.osmElementId=value["osmElementId"]
             self.osmElementType=value["osmElementType"]     
             self.osmElementTags=value["osmElementTags"]