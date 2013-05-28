# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component.factory import Factory

from plone.app.content.item import Item
from collective.cmisquery.interfaces import ICMISQuery
from plone.app.content.interfaces import INameFromTitle


class CMISQuery(Item):
    portal_type = "CMIS Query"
    implements(INameFromTitle, ICMISQuery)

    text = FieldProperty(ICMISQuery['text'])
    browser = FieldProperty(ICMISQuery['browser'])
    query = FieldProperty(ICMISQuery['query'])

    def getBrowser(self):
        # This cannot be done inside a property since acquisition is
        # disabled inside it, so the intid of self doesn't resolve.
        field = ICMISQuery['browser']
        try:
            data = field.get(self)
        except TypeError:
            raise ValueError(u"plone.app.relation is not installed")
        if data:
            return list(data[0]['objects'])[0]
        return None


CMISQueryFactory = Factory(CMISQuery, title=u"Create CMIS Query")
