#-*- coding:utf-8 -*-
import json
import logging

from django.db import models
from django.db.models.signals import post_save

from djcelery.models import PeriodicTask, IntervalSchedule

logger = logging.getLogger(__name__)


class Domain(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = u'domain'
        verbose_name_plural = 'domains'

    def __unicode__(self):
        return self.name

    def get_uptime(self):
        up_count = CheckLog.objects.filter(atc__domain=self, status=True).count()
        all_count = CheckLog.objects.filter(atc__domain=self).count()
        if up_count == 0:
            return 0
        return 100.0 * float(up_count) / float(all_count)

    def is_up(self):
        try:
            last_log_entry = CheckLog.objects.filter(atc__domain=self).order_by('created')[0]
        except:
            return False
        return last_log_entry.status


class AvailabilityTestCase(models.Model):
    GET = 'GE'
    TEST_CASE_KIND_CHOICES = (
        (GET, 'GET'),
    )
    domain = models.ForeignKey(Domain)
    kind = models.CharField(max_length=2, choices=TEST_CASE_KIND_CHOICES, default=GET)
    url = models.URLField(max_length=500)
    parameters = models.TextField(max_length=600, null=True, blank=True)
    period = models.IntegerField(u'Interval in seconds', default=15)

    def __unicode__(self):
        return '{0} {1}'.format(self.domain, self.kind)

    def create_simmetric_periodic_task(self):
        test_name = 'atc' + str(self.pk)
        if PeriodicTask.objects.filter(name=test_name).exists():
            PeriodicTask.objects.filter(name=test_name).delete()
        interval_schedule = IntervalSchedule(every=self.period, period='seconds')
        interval_schedule.save()
        PeriodicTask(name=test_name, task='pingokio.domains.tasks.process_atc', interval=interval_schedule, args=json.dumps([self.pk])).save()

    @staticmethod
    def post_save(sender, **kwargs):
        inst = kwargs['instance']
        inst.create_simmetric_periodic_task()

post_save.connect(AvailabilityTestCase.post_save, sender=AvailabilityTestCase, dispatch_uid="atc_post_save")


class CheckLog(models.Model):
    atc = models.ForeignKey(AvailabilityTestCase)
    result = models.TextField(max_length=1000, null=True, blank=True)
    status = models.BooleanField(null=False, blank=False, default=True)
    created = models.DateTimeField(auto_now_add=True)
