#-*- coding:utf-8 -*-
import logging
import urllib2

from celery import task
from celery.signals import beat_init
from djcelery.models import PeriodicTask

from pingokio.domains.models import AvailabilityTestCase, CheckLog

logger = logging.getLogger(__name__)


def get(availability_test_case_id):
    return True


@task
def post(availability_test_case_id):
    return True


@task
def ping(availability_test_case_id):
    return True


@task
def process_atc(atc_pk):
    atc = AvailabilityTestCase.objects.get(pk=atc_pk)
    if atc.kind == AvailabilityTestCase.GET:
        try:
            a = urllib2.urlopen(atc.url)
            if a.code == 200:
                CheckLog(atc=atc, result='ok', status=True).save()
            else:
                CheckLog(atc=atc, result='false', status=False).save()
        except:
            CheckLog(atc=atc, result='false', status=False).save()
    logger.debug('process atc %s' % atc.pk)


def create_periodic_tasks(sender=None, **kwargs):
    logger.info("beat_init signal")
    PeriodicTask.objects.filter(name__contains='atc').delete()
    for test in AvailabilityTestCase.objects.all():
        test.create_simmetric_periodic_task()
        logger.debug('register task for %s' % test)

beat_init.connect(create_periodic_tasks)
