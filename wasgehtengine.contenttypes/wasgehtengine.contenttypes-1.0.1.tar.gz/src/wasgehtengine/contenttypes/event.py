# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from period import IPeriod
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer import indexer
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
from venue import IVenue
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form import validator
from z3c.relationfield.schema import RelationList, RelationChoice, RelationList, \
    RelationChoice, Relation
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Invalid
from DateTime import DateTime

class IEvent(form.Schema):
    """An event
    """

    venue = RelationChoice(
                title=_("Venue"),
                description=_("Event's venue"),
                source=ObjPathSourceBinder(object_provides=IVenue.__identifier__),
                required=True,
            )

    website = schema.URI(
                title=_("Website"),
                description=_("Event's website"),
                required=False,
            )

    period = schema.Object(
                title=_("Period"),
                description=_("Time-span of the event"),
                schema=IPeriod,
                required=True,
            )

class View(grok.View):
    """Default view (called "@@view"") for an event.

    The associated template is found in event_templates/view.pt.
    """

    grok.context(IEvent)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass
