# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer.decorator import indexer
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
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

class IOsmImportStatus(form.Schema):
    """Event import status for OpenStreetMap query
    """
    
    query_params = schema.TextLine(
                title=_("Query Params"),
                description=_("OpenStreetMap XAPI Parameters"),
                required=False,
            )

    last_run = schema.Datetime(
                title=_("Last run"),    
                required=False,
            )

    last_successful_run = schema.Datetime(
                title=_("Last successful run"),    
                required=False,
            )
    
    last_run_with_venues_imported = schema.Datetime(
                title=_("Last successful run which imported venues"),    
                required=False,
            )
    
    imported_venues_count = schema.Int(
                title=_("Imported/updated venues"),
                description=_("Number of venues imported at last successful run"),
                required=False,
            )
    
class View(grok.View):
    """Default view (called "@@view"") for an osm import status item.

    The associated template is found in osmimportstatus_templates/view.pt.
    """

    grok.context(IOsmImportStatus)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass