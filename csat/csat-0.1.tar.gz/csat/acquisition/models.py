import os
import base64

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now
from django.core.urlresolvers import reverse

try:
    from PIL import Image
except ImportError:
    Image = None

from polymorphic import PolymorphicModel

from csat.acquisition import get_collector


graph_fs = FileSystemStorage(location=settings.GRAPHS_ROOT)
logs_fs = FileSystemStorage(location=settings.EXECUTION_LOGS_ROOT)


class AcquisitionSessionConfig(models.Model):

    CONFIGURED, RUNNING, COMPLETED, FAILED = range(4)

    STATUSES = {
        CONFIGURED: _('Configured'),
        RUNNING: _('Running'),
        COMPLETED: _('Completed'),
        FAILED: _('Completed with errors'),
    }

    name = models.CharField(
        max_length=64,
        help_text=_('Name this acquisition setup. Choose something you can '
                    'easily remember'))

    description = models.TextField(
        blank=True,
        help_text=_('Describe the setup, e.g. which project are you capturing '
                    'data for, from which sources,...'))

    temporary = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    thumbnail_background = models.CharField(null=True, blank=True,
                                            max_length=7)

    def __unicode__(self):
        return self.name

    def get_graph_upload_path(self, filename):
        return '{}/merged.graphml'.format(self.id)
    graph = models.FileField(upload_to=get_graph_upload_path, storage=graph_fs,
                             blank=True, null=True)

    def get_thumbnail_upload_path(self, filename):
        return 'graph-thumbnails/{}.png'.format(self.id)
    thumbnail = models.ImageField(upload_to=get_thumbnail_upload_path,
                                  blank=True, null=True)

    def get_thumbnail_url(self):
        return reverse('csat:acquisition:session-thumbnail', kwargs={
            'pk': self.pk})

    def get_graph_url(self, raw=True):
        fmt = 'graphml' if raw else 'html'
        return reverse('csat:acquisition:session-view-results', kwargs={
            'session_pk': self.pk,
            'format': fmt,
        })

    @property
    def status(self):
        if self.started is None:
            return self.CONFIGURED

        if self.completed is None:
            return self.RUNNING

        if self.collectors.filter(status=DataCollectorConfig.FAILED).count():
            return self.FAILED

        return self.COMPLETED

    def set_completed(self, save=True):
        self.completed = now()
        if save:
            self.save()

    def get_absolute_url(self):
        return reverse('csat:acquisition:session', kwargs={'pk': self.pk})

    def get_thumbnail_background(self):
        if not Image or not self.thumbnail:
            return False

        with self.thumbnail as fh:
            image = Image.open(fh)
            image = image.resize((200, 200)).convert('RGB')
            w, h = image.size
            image = image.crop((0, h - 70, w, h))
            image = image.convert('P', palette=Image.ADAPTIVE, colors=3)
            image.putalpha(0)
            colors = image.getcolors(200 * 200)
            colors = sorted(colors, reverse=True)
            color = colors[0][1]

        return '#{:02x}{:02x}{:02x}'.format(*color)

    def has_dark_thumbnail(self):
        color = self.thumbnail_background
        if not color:
            return False
        color = color[1:3], color[3:5], color[5:]
        color = [int(n, 16) for n in color]
        brightness = sum(color) / 3.0 / 255
        return brightness < 0.5

    dark_thumbnail = property(has_dark_thumbnail)

    class Meta:
        ordering = ['created']


class DataCollectorConfig(PolymorphicModel):

    READY, RUNNING, FAILED, COMPLETED = range(4)

    STATUS_CHOICES = (
        (READY, _('Ready to run')),
        (RUNNING, _('Running')),
        (FAILED, _('Failed')),
        (COMPLETED, _('Completed')),
    )

    configurator = models.CharField(max_length=44)

    session_config = models.ForeignKey(AcquisitionSessionConfig,
                                       related_name='collectors')
    started = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    running_instance_id = models.CharField(max_length=128,
                                           null=True, blank=True)
    result_id = models.CharField(max_length=64, blank=True, null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=READY)

    def __unicode__(self):
        return u'{} / {}'.format(self.session_config, self.name)

    @property
    def name(self):
        return self.get_collector().name

    def get_graph_upload_path(self, filename):
        return '{}/{}-{}.graphml'.format(self.session_config.pk, self.pk,
                                         self.configurator)
    graph = models.FileField(upload_to=get_graph_upload_path, storage=graph_fs,
                         blank=True,
                         null=True)
    #schema=graphml.get_schema_path(),

    def get_log_upload_path(self, filename):
        return '{}/{}.log'.format(self.session_config.pk, self.pk)
    output = models.FileField(upload_to=get_log_upload_path, storage=logs_fs,
                              blank=True, null=True)

    def get_graph_url(self, raw=True):
        fmt = 'graphml' if raw else 'html'
        return reverse('csat:acquisition:collector-view-results', kwargs={
            'session_pk': self.session_config.pk,
            'collector_pk': self.pk,
            'format': fmt,
        })

    def get_log_url(self, raw=True):
        fmt = 'txt' if raw else 'html'
        return reverse('csat:acquisition:collector-view-log', kwargs={
            'session_pk': self.session_config.pk,
            'collector_pk': self.pk,
            'format': fmt,
        })

    def set_running(self, save=True):
        if self.status != DataCollectorConfig.READY:
            raise RuntimeError('Collector in invalid state: {}'.format(
                self.status))
        self.status = DataCollectorConfig.RUNNING
        self.started = now()
        if save:
            self.save()

    def set_failed(self, save=True):
        if self.status not in (DataCollectorConfig.RUNNING,
                               DataCollectorConfig.READY):
            raise RuntimeError('Collector in invalid state: {}'.format(
                self.status))

        if not self.started:
            self.started = now()

        self.status = DataCollectorConfig.FAILED
        self.completed = now()

        if save:
            self.save()

    def set_completed(self, save=True):
        if self.status not in (DataCollectorConfig.RUNNING,
                               DataCollectorConfig.READY):
            raise RuntimeError('Collector in invalid state: {}'.format(
                self.status))

        if not self.started:
            self.started = now()

        self.status = DataCollectorConfig.COMPLETED
        self.completed = now()

        if save:
            self.save()

    def create_postback_url(self, save=True):
        if self.result_id:
            raise ValueError('Postback URL already defined')

        if self.status in (DataCollectorConfig.FAILED,
                           DataCollectorConfig.COMPLETED):
            raise RuntimeError('Collector in invalid state: {}'.format(
                self.status))

        self.result_id = base64.urlsafe_b64encode(os.urandom(48))

        if save:
            self.save()

        return self.get_postback_url()

    def get_postback_url(self):
        if not self.result_id:
            raise ValueError('Postback URL not yet defined')
        return reverse('csat:acquisition:collector-upload-results', kwargs={
            'result_id': self.result_id,
        })

    def get_collector(self):
        return get_collector(self.configurator)
