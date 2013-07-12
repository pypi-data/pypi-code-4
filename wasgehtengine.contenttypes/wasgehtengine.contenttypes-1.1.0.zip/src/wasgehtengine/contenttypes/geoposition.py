# -*- coding: utf-8 -*-

from plone.directives import form
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form.interfaces import IObjectFactory
from zope import schema
from zope.component import adapts
from zope.interface import Interface, implements


class IGeoPosition(Interface):
    """ A geographic position (coordinates)
    """

    latitude = schema.Float(
                title=_("Latitude"),
                description=_("Latitude"),
                required=False,
                )

    longitude = schema.Float(
                title=_("Longitude"),
                description=_("Longitude"),
                required=False,
                )

class GeoPositionFactory(object):
     adapts(Interface, Interface, Interface, Interface)
     implements(IObjectFactory)

     def __init__(self, context, request, form, widget):
         pass

     def __call__(self, value):
         return GeoPosition(value)
     
class GeoPosition(object):
     implements(IGeoPosition)

     def __init__(self, value=None):
         if value:
             self.latitude=value["latitude"]
             self.longitude=value["longitude"]