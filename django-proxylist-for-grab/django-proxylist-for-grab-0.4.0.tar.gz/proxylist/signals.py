# -*- coding: utf-8 -*-

import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from management.commands.update_proxies import ProcessFile

from models import Upload


@receiver(post_save, sender=Upload)
def insert_ips_from_file(sender, **kwargs):
    obj = kwargs['instance']
    file_name = os.path.join(settings.MEDIA_ROOT, str(obj.file_name))
    if os.path.exists(file_name):
        ProcessFile(file_name, obj.proxy_type).run()
