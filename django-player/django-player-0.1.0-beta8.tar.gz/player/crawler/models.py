from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from configfield.dbfields import JSONField
from player.crawler import get_backend, get_backends
from player.crawler.managers import ReportManager


REPORT_RETURN_CODES = (
    ('unk', _('Unknow')),
    ('suc', _('Success')),
    ('err', _('Error')),
    ('net', _('New elements treshold exceeded')),
    ('met', _('Modified elements treshold exceeded')),
    ('det', _('Deleted elements treshold exceeded')),
)


class Report(models.Model):
    crawler_collection = models.ForeignKey('CrawlerCollection')
    crawling_time = models.DateTimeField(
        _('Crawling time'),
        null=True,
        blank=True,
    )
    return_code = models.CharField(
        _('Return code'),
        max_length=3,
        choices=REPORT_RETURN_CODES,
    )
    traceback = models.TextField(
        _('Traceback'),
        blank=True,
        null=True,
    )
    crawled_data = models.TextField(
        _('Crawled data'),
    )
    added_items = models.ManyToManyField(
        'data.Item',
        blank=True,
        null=True,
        related_name='added_in_reports',
    )
    updated_items = models.ManyToManyField(
        'data.Item',
        blank=True,
        null=True,
        related_name='updated_in_reports',
    )
    deleted_items_json = JSONField(
        blank=True,
        null=True,
    )

    objects = ReportManager()

    class Meta:
        get_latest_by = 'crawling_time'
        ordering = ('-crawling_time', )

    def __unicode__(self):
        return u'%s (%s)' % (self.crawler_collection, self.crawling_time.strftime('%d/%m/%Y %H:%M:%S'))

    @models.permalink
    def get_absolute_url(self):
        return ('report_view', (self.id, ))


class CrawlerCollection(models.Model):
    """ Represent a scraping tool content type (news, events, etc) """
    backend = models.CharField(max_length=200,
                               choices=get_backends(),
                               help_text=_('Unique code for integrating with extraction tool collection'))
    collection_code = models.CharField(max_length=200,
                                       help_text=_('Unique code for integrating with extraction tool collection'))
    schema = JSONField(editable=False)
    last_crawling_time = models.DateTimeField(_('Last crawling time'),
                                              null=True, blank=True)
    last_job_time = models.DateTimeField(_('Last job made in extraction tool'),
                                         null=True, blank=True)

    check_deleted = models.BooleanField(_('Check deleted'), default=False)
    # this threshold values are CharField instead of Integer to allow percentages
    new_elements_threshold = models.CharField(_('Maximum number of new elements'),
        max_length=200, null=True, blank=True)
    modified_elements_threshold = models.CharField(_('Maximum number of modified elements'),
        max_length=200, null=True, blank=True)
    deleted_elements_threshold = models.CharField(_('Maximum number of deleted elements'),
        max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _('Crawler collection')

    def __unicode__(self):
        return self.collection_code


def handle_collection_save(sender, instance, created, **kwargs):
    if created:
        get_backend(instance.backend).load_collection_schema(instance)

post_save.connect(handle_collection_save, sender=CrawlerCollection)
