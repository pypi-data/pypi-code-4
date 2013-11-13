"""A slightly user-friendly API for portal_repository."""
from Products.CMFCore.utils import getToolByName

def is_versionable(context, type_id):
    portal_repository = getToolByName(context, 'portal_repository')
    return type_id in portal_repository.getVersionableContentTypes()
    
def get_versioning_policies_for_type(context, type_id):
    """Return: a set of versioning policies IDs."""
    portal_repository = getToolByName(context, 'portal_repository')
    return set(portal_repository.getPolicyMap().get(type_id, tuple()))

def toggle_versioning_for_type(context, type_id, enable):
    """
    Enable or disable versioning for a type. This function will NOT raise an
    error if you try to enable versioning for a type which is already
    enabled or vice-versa. 
    """
    portal_repository = getToolByName(context, 'portal_repository')
    type_set = set([type_id])
    versionable_types = set(portal_repository.getVersionableContentTypes())
    if enable:
        versionable_types |= type_set
    else:
        versionable_types -= type_set        
    
    portal_repository.setVersionableContentTypes(list(versionable_types))

def set_versioning_policies_for_type(context, type_id, policies):
    """
    Set the versioning policies for a type.
    
    Arguments:
    type_id -- The type ID.
    policies -- A set of versioning policies.
    """    
    portal_repository = getToolByName(context, 'portal_repository')    
    current_policies = get_versioning_policies_for_type(context, type_id)
    
    for policy in policies - current_policies:
        portal_repository.addPolicyForContentType(type_id, policy)
    
    for policy in current_policies - policies:
        portal_repository.removePolicyFromContentType(type_id, policy)