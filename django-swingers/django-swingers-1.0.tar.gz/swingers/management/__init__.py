from django.db.models.signals import post_syncdb
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


def add_view_permissions(sender, **kwargs):
    """
    This syncdb hook takes care of adding a view permission to all our
    content types.
    """
    for content_type in ContentType.objects.all():
        codename = "view_%s" % content_type.model
        if not Permission.objects.filter(content_type=content_type,
                                         codename=codename):
            Permission.objects.create(content_type=content_type,
                                      codename=codename,
                                      name="Can view %s" % content_type.name)


# check for all our view permissions after a syncdb
post_syncdb.connect(add_view_permissions)
