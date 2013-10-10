# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from zope.interface import implements
import interfaces
from Products.Doormat.content.DoormatMixin import DoormatMixin

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.Doormat.config import PROJECTNAME

schema = atapi.Schema((


),
)

DoormatColumn_schema = ATFolderSchema.copy() + \
    getattr(DoormatMixin, 'schema', atapi.Schema(())).copy() + \
    schema.copy()


class DoormatColumn(ATFolder, DoormatMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDoormatColumn)

    meta_type = 'DoormatColumn'
    _at_rename_after_creation = True

    schema = DoormatColumn_schema


atapi.registerType(DoormatColumn, PROJECTNAME)
