# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
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
from plone.app.layout.navigation.interfaces import INavigationRoot
from DateTime import DateTime
from datetime import timedelta
from datetime import datetime
import iso8601
from venuefolder import IVenueFolder
from eventfolder import IEventFolder

class SiteRootView(grok.View):

    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('wasgehtengine_homepage')
    
    def update(self):
        pass