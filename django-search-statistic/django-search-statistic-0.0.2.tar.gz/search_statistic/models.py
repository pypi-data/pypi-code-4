# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from search_statistic.utils.search_engine import search_engine_choices

import cPickle


class WithVisitsManager(models.Manager):
    def get_query_set(self):
        return super(WithVisitsManager, self).get_query_set().annotate(
            visits_amount=models.Sum('visit__amount')
        ).order_by('-visits_amount')


class SearchQuery(models.Model):

    objects = WithVisitsManager()
    default = models.Manager()

    query = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_(u'query'),
        unique=True,
        null=False,
        blank=False
    )
    confirm = models.BooleanField(
        verbose_name=_(u'is confirmed?'),
        null=False,
        blank=False,
        default=False
    )

    def __unicode__(self):
        return self.query

    @property
    def visits(self):
        return self.visit_set.aggregate(
            visits=models.Sum('amount')
        ).get('visits', 0)

    class Meta:
        verbose_name = _(u'search query')
        verbose_name_plural = _(u'search queries')


class Visit(models.Model):

    query = models.ForeignKey(
        'SearchQuery',
        verbose_name=_(u'search query'),
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )
    path = models.CharField(
        max_length=255,
        verbose_name=_(u'visited url path'),
        db_index=True,
        null=False,
        blank=False
    )
    content_type = models.CharField(
        max_length=127,
        verbose_name=_(u'content type of visited object'),
        null=True,
        blank=True
    )
    object_pk = models.IntegerField(
        verbose_name=_(u'object primary key'),
        null=True,
        default=None
    )
    search_engine = models.CharField(
        max_length=15,
        verbose_name=_(u'search engine'),
        null=False,
        blank=False,
        choices=search_engine_choices()
    )
    amount = models.IntegerField(
        verbose_name=_(u'number of visits'),
        null=False,
        blank=False,
        default=1
    )
    timestamp = models.DateTimeField(
        verbose_name=_(u'visits time'),
        null=False,
        blank=False,
        auto_now=False,
        auto_now_add=True
    )

    @classmethod
    def top(cls):
        query = cls.objects.all().query
        query.group_by = ['path', 'query_id']
        qs = models.query.QuerySet(query=query, model=cls).annotate(
            whole_amount=models.Sum('amount')
        ).filter(query__confirm=True).order_by('-amount')
        return qs

    def __unicode__(self):
        return u'{}: {} ==>> {}'.format(
            self.search_engine.title() if self.search_engine else '...',
            self.query if self.query_id else '...',
            self.url
        )

    @property
    def url(self):
        obj = self.visited_object
        if obj and hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return self.path

    @property
    def visited_object(self):
        return self.get_object(self.content_type, self.object_pk)

    @staticmethod
    def get_object(content_type, object_pk):
        if not content_type:
            return
        try:
            content_type = cPickle.loads(str(content_type))
        except AttributeError:
            return
        if issubclass(content_type, models.Model):
            try:
                return content_type.objects.get(pk=object_pk)
            except content_type.DoesNotExist:
                return
        else:
            return content_type

    class Meta:
        verbose_name = _(u'visit')
        verbose_name_plural = _(u'visits')
        ordering = ['-timestamp']
