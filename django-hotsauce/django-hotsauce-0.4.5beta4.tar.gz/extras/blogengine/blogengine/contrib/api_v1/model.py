#!/usr/bin/env python
# Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# -*- coding: utf-8 -*-
# <LICENSE=ISC>
# Default model classes for use in BlogEngine
from notmm.dbapi.orm import RelationProxy, XdserverProxy
from notmm.utils.django_settings import LazySettings

_settings = LazySettings()
db = XdserverProxy(_settings.SCHEVO['DATABASE_NAME'])

class CategoryManager(object):
    """
    >>> categories = CategoryManager.objects.all()
    []
    >>> CategoryManager.objects.count()
    0
    """

    objects = RelationProxy(db.Category)

    def __repr__(self):
        return "<CategoryManager: %s>" % self.objects.name

class CategoryItemManager(object):
    objects = RelationProxy(db.CategoryItem)

class BlogEntryManager(object):
    objects = RelationProxy(db.BlogEntry)

    def get_published_posts(self, params=[], order_by='pub_date'):
        """
        Fetch blog posts using custom selection filters
        
        params = [('reviewed', '==', True), ...]

        """
        lst = []
        for param, direction, value in params:
            q = db.Q.Match(db.BlogEntry, param, direction, value)
            lst.append(q)

        results = db.Q.Intersection(*lst)
        return [item for item in results()] #self.objects.find(**results())

EntryManager = BlogEntryManager

class CommentManager(object):
    objects = RelationProxy(db.Comment)
    
    #def__new__(cls, *args, **kwargs):
    #   cls.feedobj = cls.create_feed_obj(metaclass=RSSFeedGenerator)
    #
    #def create_feed_obj(self, metaclass):
    #   pass

class MessageManager(object):
    objects = RelationProxy(db.Message)

# Generic voting Manager objects
#class PollManager(object):
#    objects = RelationProxy(db.Poll)

