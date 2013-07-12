# -*- coding: utf-8 -*-

from plone.directives import form
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form.interfaces import IObjectFactory
from zope import schema
from zope.component import adapts
from zope.interface import Interface, implements


class IPeriod(Interface):
    """ A time-span
    """

    start = schema.Datetime(
                title=_("Start"),
                description=_("Start date/time"),    
                required=True,
            )

    end = schema.Datetime(
                title=_("End"),
                description=_("End date/time"),    
                required=True,
            )
    
    no_starttime = schema.Bool(
                title=_("No start time"),
                description=_("Whether a precise start time is given or not"),
                required=True,
                default=False,
    )
    
    no_endtime = schema.Bool(
                title=_("No end time"),
                description=_("Whether a precise end time is given or not"),
                required=True,
                default=False,                           
    )

class PeriodFactory(object):
     adapts(Interface, Interface, Interface, Interface)
     implements(IObjectFactory)

     def __init__(self, context, request, form, widget):
         pass

     def __call__(self, value):
         return Period(value)
     
class Period(object):
     implements(IPeriod)

     def __init__(self, value = None):
         
         if value is None:
             pass
         else:
             self.start=value["start"]
             self.end=value["end"]
             self.no_starttime=['no_starttime']
             self.no_endtime=['no_endtime']