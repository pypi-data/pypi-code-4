# -*- coding: utf-8 -*-
#
#
# Copyright (c) 2010 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
from zope.interface import Interface

##code-section module-header #fill in your manual code here
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.CMFPlone import PloneMessageFactory as _

##/code-section module-header

from config import *

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

TCContentReference_schema = ATContentTypeSchema.copy() + \
    schema.copy()

TCContentReference_schema['title'].required=0
TCContentReference_schema['title'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['description'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['subject'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['location'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['rights'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['contributors'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['creators'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['allowDiscussion'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['creators'].widget.visible={'edit':'invisible', 'view':'invisible'}
TCContentReference_schema['creation_date'].widget.visible={'edit':'invisible', 'view':'invisible'}

TCContentReference_schema.changeSchemataForField('relatedItems', 'default')
TCContentReference_schema.changeSchemataForField('language', 'settings')

##code-section after-schema #fill in your manual code here

##/code-section after-schema


##code-section HEAD
##/code-section HEAD

class ITCContentReference(Interface):
    """Marker interface for .stammdaten.Stammdaten
    """

class TCContentReference(ATCTContent):
    """
    """
    security = ClassSecurityInfo()

    implements(ITCContentReference)

    meta_type = 'ITCContentReference'
    _at_rename_after_creation = True

    schema = TCContentReference_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods
    def Title(self):
        """Return the title of the original"""
        for object_ in self.getRelatedItems():
            return object_.Title()
        return ''

    def SearchableText(self):
        """Return the SearchableText of the original"""
        string_=''

        for object_ in self.getRelatedItems():
            string_+=object_.SearchableText()

        return string_

registerType(TCContentReference, PROJECTNAME)
# end of class TCBlog

##code-section module-footer #fill in your manual code here
##/code-section module-footer



