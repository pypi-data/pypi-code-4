from zope.security import checkPermission as has_permission
from plone.autoform.interfaces import READ_PERMISSIONS_KEY


def get_read_permissions(schema):
    return schema.queryTaggedValue(READ_PERMISSIONS_KEY, {})


def set_read_permissions(schema, permissions):
    return schema.setTaggedValue(READ_PERMISSIONS_KEY, permissions)


def has_read_access(schema, field, context):

    required_permission = get_read_permissions(schema).get(field)

    if required_permission:
        return has_permission(required_permission, context)
    else:
        return True
