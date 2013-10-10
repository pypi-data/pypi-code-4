# -*- coding: utf-8 -*-
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "Doormat"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))
ADD_CONTENT_PERMISSIONS = {
    'Doormat': 'Doormat: Add Doormat',
    'DoormatColumn': 'Doormat: Add DoormatColumn',
    'DoormatSection': 'Doormat: Add DoormatSection',
    'DoormatReference': 'Doormat: Add DoormatReference',
    'DoormatMixin': 'Doormat: Add DoormatMixin',
    'DoormatCollection': 'Doormat: Add DoormatCollection',
}

setDefaultRoles('Doormat: Add Doormat', ('Manager', 'Owner'))
setDefaultRoles('Doormat: Add DoormatColumn', ('Manager', 'Owner'))
setDefaultRoles('Doormat: Add DoormatSection', ('Manager', 'Owner'))
setDefaultRoles('Doormat: Add DoormatReference', ('Manager', 'Owner'))
setDefaultRoles('Doormat: Add DoormatMixin', ('Manager', 'Owner'))
setDefaultRoles('Doormat: Add DoormatCollection', ('Manager', 'Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []
