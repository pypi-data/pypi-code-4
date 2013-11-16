# -*- coding: utf-8 -*-
"""Define your models in this module.

Models are standard Python classes which inherits from
:class:`django.db.models.Model`. A model represents a SQL table.

Documentation can be found at .

"""
from heapq import heappop, heappush
import os
import shutil
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
__author__ = "flanker"


class ObjectCache(object):

    def __init__(self, cache_miss_fn, limit=1000):
        self.obj_key = {}
        self.key_list = []
        self.limit = limit
        self.cache_miss_fn = cache_miss_fn

    def get(self, key):
        if key in self.obj_key:
            return self.obj_key[key]
        obj = self.cache_miss_fn(key)
        self.obj_key[key] = obj
        heappush(self.key_list, key)
        if len(self.key_list) > self.limit:
            key = heappop(self.key_list)
            del self.obj_key[key]
        return obj


class Keyword(models.Model):
    value = models.CharField(_('keyword'), max_length=255, db_index=True)
    __cache = None

    def __str__(self):
        return self.value

    @classmethod
    def get(cls, name):
        if cls.__cache is None:
            cls.__cache = ObjectCache(lambda key: cls.objects.get_or_create(value=key)[0])
        return cls.__cache.get(name)


class UploadDoc(models.Model):
    uid = models.CharField(_('uid'), max_length=50, db_index=True)
    name = models.CharField(_('title'), max_length=255, db_index=True, default='')
    path = models.CharField(_('path'), max_length=255, db_index=True)
    keywords = models.ManyToManyField(Keyword, db_index=True, blank=True)
    user = models.ForeignKey(User, db_index=True, null=True, blank=True)
    upload_time = models.DateTimeField(_('upload time'), db_index=True, auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(UploadDoc, self).__init__(*args, **kwargs)
        self.__index = None

    def __str__(self):
        return self.name

    class Meta:
        """Meta informations on this model"""
        verbose_name = _('sample person')
        verbose_name_plural = _('sample persons')

    @property
    def index(self):
        if self.__index is None:
            self.__index = ''
            for index in ('index.html', 'index.htm'):
                if os.path.isfile(os.path.join(self.path, 'index.html')):
                    self.__index = index
                    break
        return self.__index

    def delete(self, using=None):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        super(UploadDoc, self).delete(using=using)


class LastDocs(models.Model):
    doc = models.ForeignKey(UploadDoc, db_index=True)
    user = models.ForeignKey(User, db_index=True, null=True, blank=True)
    count = models.IntegerField(db_index=True, blank=True, default=1)
    last = models.DateTimeField(_('last'), db_index=True, auto_now=True)
