from Products.CMFCore.permissions import setDefaultRoles

setDefaultRoles('mediasearch: view', ('Manager',))

def initialize(context):
    pass