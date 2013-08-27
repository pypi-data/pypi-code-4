from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.contrib.auth.models import Permission
from pgauth.models import Role
from pgauth.settings import USER_ROLE_ID, OWNER_ROLE_ID
from djinn_events import models


def create_permissions(**kwargs):
    
    contenttype = ContentType.objects.get(
        app_label='djinn_events', 
        model='event')

    role_user = Role.objects.get(name=USER_ROLE_ID)
    role_owner = Role.objects.get(name=OWNER_ROLE_ID)

    add, created = Permission.objects.get_or_create(
        codename="add_event", 
        content_type=contenttype, 
        defaults={'name': 'Add event'})

    edit, created = Permission.objects.get_or_create(
        codename="change_event", 
        content_type=contenttype, 
        defaults={'name': 'Change event'})

    delete, created = Permission.objects.get_or_create(
        codename="delete_event", 
        content_type=contenttype, 
        defaults={'name': 'Delete event'})

    role_user.add_permission_if_missing(add)
    role_owner.add_permission_if_missing(edit)
    role_owner.add_permission_if_missing(delete)


signals.post_syncdb.connect(create_permissions, sender=models)
