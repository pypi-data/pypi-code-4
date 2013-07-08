from djinn_announcements import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.contrib.auth.models import Permission
from pgauth.models import Role
from pgauth.settings import USER_ROLE_ID, OWNER_ROLE_ID


def create_permissions(**kwargs):
    
    announcement = ContentType.objects.get(
        app_label='djinn_announcements', 
        model='announcement')

    service_announcement = ContentType.objects.get(
        app_label='djinn_announcements', 
        model='serviceannouncement')

    role_owner = Role.objects.get(name=OWNER_ROLE_ID)

    add, created = Permission.objects.get_or_create(
        codename="add_announcement", 
        content_type=announcement, 
        defaults={'name': 'Add annnouncement'})

    edit, created = Permission.objects.get_or_create(
        codename="change_announcement", 
        content_type=announcement, 
        defaults={'name': 'Change announcement'})

    delete, created = Permission.objects.get_or_create(
        codename="delete_announcement", 
        content_type=announcement, 
        defaults={'name': 'Delete announcement'})

    role_owner.add_permission_if_missing(edit)
    role_owner.add_permission_if_missing(delete)

    add, created = Permission.objects.get_or_create(
        codename="add_serviceannouncement", 
        content_type=service_announcement, 
        defaults={'name': 'Add service annnouncement'})

    edit, created = Permission.objects.get_or_create(
        codename="change_serviceannouncement", 
        content_type=service_announcement, 
        defaults={'name': 'Change service announcement'})

    delete, created = Permission.objects.get_or_create(
        codename="delete_serviceannouncement", 
        content_type=service_announcement, 
        defaults={'name': 'Delete service announcement'})

    role_owner.add_permission_if_missing(edit)
    role_owner.add_permission_if_missing(delete)


signals.post_syncdb.connect(create_permissions, sender=models)
