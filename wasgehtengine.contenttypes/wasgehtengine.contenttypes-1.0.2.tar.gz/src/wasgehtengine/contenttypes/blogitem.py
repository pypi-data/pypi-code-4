# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from period import IPeriod
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
from Products.CMFDefault.interfaces import INewsItem
from DateTime import DateTime
from datetime import timedelta
from datetime import datetime
from zope.interface import Interface
import iso8601

class BlogItemView(grok.View):

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('blog_item')
    
    def update(self):
        pass