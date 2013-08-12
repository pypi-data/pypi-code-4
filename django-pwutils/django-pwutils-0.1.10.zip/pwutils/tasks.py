# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from pwutils.utils import celery_task

send_mail = celery_task(name='pwutils.send_mail',
                        ignore_result=True)(send_mail)
