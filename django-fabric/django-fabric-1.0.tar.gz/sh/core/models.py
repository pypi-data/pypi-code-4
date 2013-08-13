# -*- coding: utf-8 -*-
from datetime import datetime
from random import choice
from django.conf import settings
from django.contrib.auth.models import User
import string
from django.core.mail import send_mail
from django.db import models
from sh.core import auth

from django.contrib.contenttypes.models import ContentType

class UserProxy(User):
    class Meta:
        proxy = True

    def generate_password(self, length=8, notify=True, chars=string.letters + string.digits):
        pw = ''.join([choice(chars) for i in range(length)])
        self.set_password(pw)
        self.save()
        if notify:
            message = 'Your password is: %s' % pw
            send_mail('Your password', message, settings.EMAIL_HOST_USER, (self.email,))
            #Todo: Need notification-system first


class BaseModel (models.Model):
    created_by = models.ForeignKey(User, related_name="%(class)s_creator", editable=False)
    saved_by = models.ForeignKey(User, related_name="%(class)s_saved_by", editable=False)
    date_created = models.DateTimeField(editable=False)
    date_saved = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.created_by.username + ' ' + str(self.id)

    def save(self, notify_subscribers=True, *args, **kwargs):
        user = auth.get_current_user()
        if not user or not user.is_authenticated():
            user = User.objects.get(pk=1) #dummy user
        if not self.pk:
            self.created_by = user
            self.date_created = datetime.now()
        self.saved_by = user
        self.date_saved = datetime.now()
        super(BaseModel, self).save(*args,**kwargs)


    def get_absolute_url(self):
        c_type = ContentType.objects.get_for_model(self)
        return '/%s/%ss/%s/' % (str(c_type.app_label), str(c_type), str(self.pk))

    class Meta:
        abstract = True

    @classmethod
    def exclude_fields(cls):
        return ('created_by', 'saved_by', 'date_created', 'date_saved')