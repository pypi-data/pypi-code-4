# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.Doormat.config import PROJECTNAME
from Products.Doormat.content.DoormatMixin import DoormatMixin
from zope.interface import implements

import interfaces

schema = atapi.Schema((


),
)

DoormatSection_schema = ATFolderSchema.copy() + \
    getattr(DoormatMixin, 'schema', atapi.Schema(())).copy() + \
    schema.copy()


class DoormatSection(ATFolder, DoormatMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDoormatSection)

    meta_type = 'DoormatSection'
    _at_rename_after_creation = True

    schema = DoormatSection_schema


atapi.registerType(DoormatSection, PROJECTNAME)
