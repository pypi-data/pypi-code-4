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
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form import validator
from z3c.relationfield.schema import RelationList, RelationChoice, RelationList, \
    RelationChoice, Relation
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Invalid
from DateTime import DateTime

class IMovie(form.Schema):
    """A movie
    """

    website = schema.URI(
                title=_("Website"),
                description=_("Movie's website"),
                required=False,
            )
    
    imdb_id = schema.ASCIILine(
                title=_("IMDb ID"),
                description=_("Movie's ID in IMDb"),
                required=False,
            )
    
    trailer = schema.URI(
                title=_("Trailer"),
                description=_("Trailer for the movie"),
                required=False,
            )
    
class View(grok.View):
    """Default view (called "@@view"") for a movie

    The associated template is found in movie_templates/view.pt.
    """

    grok.context(IMovie)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass