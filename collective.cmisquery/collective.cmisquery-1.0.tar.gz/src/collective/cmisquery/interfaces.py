# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope.schema import Text
from infrae.plone.relations.schema import PloneRelation
from zope.interface import Interface


class ICMISQuery(Interface):
    text = Text(
        title=u"Text",
        description=u"Text display before the results",
        required=False)
    browser = PloneRelation(
        title=u"Browser",
        description=u"CMIS Browser object to use in order to query for results",
        unique=True,
        max_length=1,
        relation="cmisbrowser")
    query = Text(
        title=u"Query",
        description=u"CMIS Query",
        default=u"SELECT R.* FROM cmis:document R WHERE CONTAINS('test')",
        required=True)

    def getBrowser():
        """Return the currently configured browser, or None
        """
