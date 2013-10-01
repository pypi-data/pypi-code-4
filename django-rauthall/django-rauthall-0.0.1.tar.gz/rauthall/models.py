# -*- coding: utf-8 -*-

import time
import socket
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings as conf
from django.db.models.signals import post_save

class UserProfile(models.Model):

    """
    UserProfile (extending Users), signals:
     - http://stackoverflow.com/questions/1910359/creating-a-extended-user-profile
    """

    user = models.OneToOneField(User)
    twitter = models.CharField(_('Twitter'), max_length=55, blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to='uploads/avatars/', blank=True)
    signature = models.TextField(_('Signature'), blank=True, default='')

    class Meta:
        verbose_name = _('Perfil de usuario')
        verbose_name_plural = _('Perfiles de usuario')

    def __unicode__(self):
        return "%s-@%s"%(self.user, self.twitter)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)