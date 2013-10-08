# -*- coding: utf-8 -*-

"""
Models for the "forum" project
"""

import time
import socket
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from datetime import datetime

class Forum(models.Model):

    """
    Forum model
    """

    moderators = models.ManyToManyField(User, blank=True, null=True, verbose_name=_('Moderators'))
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), max_length=200)
    description = models.TextField(_('Description'), blank=True, default='')
    date_created = models.DateTimeField(_('Date Created'))
    date_modified = models.DateTimeField(_('Date Modified'),auto_now_add=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    topic_count = models.IntegerField(_('Topic count'), blank=True, default=0)
    order = models.IntegerField(_('Order'), blank=True, default=0)
    status =  models.BooleanField(_('Status'), default=True)
    visible =  models.BooleanField(_('Visible'), default=True)

    def __unicode__(self):
        return self.slug

    class Meta:
        ordering = ['order']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')


class Topic(models.Model):

    """
    Topic model
    """

    user = models.ForeignKey(User, related_name="topics")
    forum = models.ForeignKey(Forum, related_name='topics', verbose_name=_('Forum'))
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), max_length=200)
    date_created = models.DateTimeField(_('Date Created'))
    date_modified = models.DateTimeField(_('Date Modified'),auto_now_add=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    topic_count = models.IntegerField(_('Topic count'), blank=True, default=0)
    hits = models.IntegerField(_('Hits'), blank=True, default=1)
    status =  models.BooleanField(_('Status'), default=True)
    sticky = models.BooleanField(_('Sticky'), blank=True, default=False)
    closed = models.BooleanField(_('Closed'), blank=True, default=False)
    subscribers = models.ManyToManyField(User, blank=True, null=True, verbose_name=_('Subscribers'))

    def __unicode__(self):
        return "%s (%s)"%(self.slug, self.forum)

    def save(self, *args, **kwargs):
        self.date_modified = datetime.now()
        super(Topic, self).save()

    def add_subscriber(self, myuser):
        self.subscribers.add(myuser)

    def del_subscriber(self, myuser):
        self.subscribers.delete(myuser)

    class Meta:
        ordering = ['-sticky', '-date_modified']
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')


class Post(models.Model):

    """
    Post model
    """

    user = models.ForeignKey(User, related_name="posts")
    topic = models.ForeignKey(Topic, related_name='posts', verbose_name=_('Topic'))
    date_created = models.DateTimeField(_('Date Created'))
    date_modified = models.DateTimeField(_('Date Modified'),auto_now_add=True)
    body = models.TextField(_('Message'))
    status =  models.BooleanField(_('Status'), default=True)
    user_ip = models.IPAddressField(_('User IP'), blank=True, null=True)

    def __unicode__(self):
        return self.body

    def save(self, *args, **kwargs):
        self.user_ip = socket.gethostbyname(socket.gethostname())
        self.date_modified = datetime.now()
        super(Post, self).save()

    class Meta:
        ordering = ['date_created']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')


class Rank(models.Model):

    """
    Rank model
    """

    limit_from = models.IntegerField(_('Limit from'), blank=True, default=1)
    limit_to = models.IntegerField(_('Limit to'), blank=True, default=1)
    rank = models.CharField(_('Rank name'), max_length=80, blank=True)

    class Meta:
        verbose_name = _('Ranking')
        verbose_name_plural = _('Rankings')

    def __unicode__(self):
        return self.rank


class Log(models.Model):

    """
    Log model
    """

    user = models.ForeignKey(User, related_name="log")
    action = models.CharField(_('Action'), max_length=255)
    date = models.DateTimeField(_('Date Created'))
    user_ip = models.IPAddressField(_('User IP'), blank=True, null=True)

    def save(self, *args, **kwargs):
        self.user_ip = socket.gethostbyname(socket.gethostname())
        self.date = datetime.now()
        super(Log, self).save()

    class Meta:
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')

    def __unicode__(self):
        return self.action
