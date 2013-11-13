from Products.CMFCore.utils import getToolByName

def get_password(context, member_id):
    """Return the password for the given member or None if cannot fetch it."""
    acl_users = getToolByName(context, 'acl_users')
    user = acl_users.getUser(member_id)
    return getattr(user, '__', None)    

def create_dict_from_member_obj(context, member):
    """
    Create a dict representation of a member object (as returned by
    portal_membership).    
    """    
    memberdata = getToolByName(context, 'portal_memberdata')
    properties = dict(
        (k, member.getProperty(k)) for k in memberdata.propertyIds()
    )
    
    member_id = member.getId()
    
    return dict(
        properties,
        id=member_id,
        password=get_password(context, member_id),
        roles=member.getRoles(),
    )

def create_dict_from_member_id(context, member_id):
    mtool = getToolByName(context, 'portal_membership')
    return create_dict_from_member_obj(context, mtool.getMemberById(member_id))

def create_member_from_dict(context, d):
    mtool = getToolByName(context, 'portal_membership')
    
    d = dict(d)    
    id = d.pop('id')
    password = d.pop('password')
    roles = d.pop('roles')    
    mtool.addMember(id, password, roles, '', d)
    
    return mtool.getMemberById(id)