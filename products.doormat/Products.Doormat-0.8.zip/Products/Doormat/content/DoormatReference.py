# -*- coding: utf-8 -*-
#
# File: DoormatReference.py
#
# Copyright (c) 2011 by unknown <unknown>
# Generator: ArchGenXML Version 2.6
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.base import ATCTContent
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Doormat.config import *

# additional imports from tagged value 'import'
try:
    from archetypes.referencebrowserwidget import ReferenceBrowserWidget
    ReferenceBrowserWidget  # pyflakes
except ImportError:
    # BBB for Plone 3 and earlier.
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    ReferenceField(
        name='internal_link',
        widget=ReferenceBrowserWidget(
            label='Internal_link',
            label_msgid='Doormat_label_internal_link',
            i18n_domain='Doormat',
        ),
        relationship="internally_links_to",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

DoormatReference_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema


class DoormatReference(ATCTContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDoormatReference)

    meta_type = 'DoormatReference'
    _at_rename_after_creation = True

    schema = DoormatReference_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(DoormatReference, PROJECTNAME)
# end of class DoormatReference

##code-section module-footer #fill in your manual code here
##/code-section module-footer
