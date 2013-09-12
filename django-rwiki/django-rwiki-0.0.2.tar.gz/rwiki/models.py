# -*- coding: utf-8 -*-

"""
Models
"""

import time
import socket
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django.conf import settings as conf


class Page(models.Model):

    """
    Page model
    """

    title = models.CharField(_(u'Title'), max_length=255)
    slug = models.CharField(_(u'Slug'), max_length=200)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_(u'Created'))
    text = models.TextField(_(u'Text'))
    hits = models.IntegerField(_(u'Hits'), default=0)
    status =  models.BooleanField(_(u'Status'), default=True)
    public =  models.BooleanField(_(u'Public'), default=True, help_text="Public pages are shown to everyone, privates only to admin user role")
    template = models.CharField(_(u'Render template'), max_length=100,
        choices=conf.RWIKI_TEMPLATES, blank=True)
    owner = models.ForeignKey(User, verbose_name=_(u'Owner'),
                              blank=True, null=True, related_name='owner')

    def __unicode__(self):
        return self.slug

    class Meta:
        verbose_name = _(u'Page')
        verbose_name_plural = _(u'Pages')
        permissions = (
            ("reverse", "Can reverse a version"),
        )
