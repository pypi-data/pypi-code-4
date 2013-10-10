# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import ATCTContent
from zope.interface import implements
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Doormat.config import PROJECTNAME

import interfaces

try:
    from archetypes.referencebrowserwidget import ReferenceBrowserWidget
    ReferenceBrowserWidget  # pyflakes
except ImportError:
    # BBB for Plone 3 and earlier.
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
        ReferenceBrowserWidget

schema = atapi.Schema((

    atapi.ReferenceField(
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

DoormatReference_schema = atapi.BaseSchema.copy() + \
    schema.copy()


class DoormatReference(ATCTContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDoormatReference)

    meta_type = 'DoormatReference'
    _at_rename_after_creation = True

    schema = DoormatReference_schema


atapi.registerType(DoormatReference, PROJECTNAME)
