# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.Archetypes.atapi import Schema, registerType
from Products.Doormat.content.DoormatMixin import DoormatMixin
from Products.Doormat.config import PROJECTNAME
from zope.interface import implements

import interfaces

schema = Schema((


),
)

Doormat_schema = ATFolderSchema.copy() + \
    getattr(DoormatMixin, 'schema', Schema(())).copy() + \
    schema.copy()


class Doormat(ATFolder, DoormatMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDoormat)

    meta_type = 'Doormat'
    _at_rename_after_creation = True

    schema = Doormat_schema


registerType(Doormat, PROJECTNAME)
