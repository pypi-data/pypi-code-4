# -*- coding: utf-8 -*-

"""
Models for the "flatpages" project
"""

import time
import socket
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django.conf import settings as conf


class Photo(models.Model):

    """
    Modelo que define una foto.
    """

    image = models.ImageField(_('Imagen'), upload_to='uploads/photos/', blank=True)
    origen = models.CharField(_('Archivo origen'), max_length=255)
    insert_date = models.DateTimeField(_(u'Fecha de inserción'))
    capture_date = models.DateTimeField(_(u'Fecha de la foto'))
    status =  models.BooleanField(_('Status'), default=True)

    def __unicode__(self):
        return str(self.image)

    class Meta:
        verbose_name = _('Foto')
        verbose_name_plural = _('Fotos')


class Video(models.Model):

    """
    Modelo que define un video.
    """

    title = models.CharField(_('Title'), max_length=255)
    image = models.ImageField(_('Imagen'), upload_to='uploads/photos_videos/', blank=True)
    video = models.FileField(_('Video'), upload_to='uploads/videos/', blank=True)
    origen = models.CharField(_('Archivo origen'), max_length=255)
    insert_date = models.DateTimeField(_(u'Fecha de inserción'))
    capture_date = models.DateTimeField(_(u'Fecha de la foto'))
    status =  models.BooleanField(_('Status'), default=True)

    def __unicode__(self):
        return str(self.title)

    class Meta:
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')
