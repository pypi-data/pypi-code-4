import logging
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
import os
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django_queue_mailer import defaults
from pytz import utc
from django.utils.timezone import utc
from django.core.mail.message import make_msgid
from django.conf import settings
from django_queue_mailer.sentry import get_raven


logger = logging.basicConfig()


def explode_addresses(addresses):
    if ',' in addresses:
        return [email.strip() for email in addresses.split(',')]
    else:
        return [addresses, ]


class QueueManager(models.Manager):
    def send_queued(self, limit=None):
        if limit is None:
            limit = getattr(settings, 'DJANGO_QUEUE_MAILER_LIMIT', defaults.DJANGO_QUEUE_MAILER_LIMIT)

        for queue in self.order_by('id')[:limit]:
            try:
                queue.send()

            except Exception, e:
                queue.deferred = True
                queue.save()

                client = get_raven()
                if client:
                    client.capture(
                        'raven.events.Message',
                        message='Deferring message with id: %s' % queue.id,
                        extra={
                            'message': e.message,
                        })

    def clear_sent_messages(self, offset=None):
        """ Deletes sent MailerMessage records """
        if offset is None:
            offset = getattr(settings, 'DJANGO_QUEUE_MAILER_OFFSET', defaults.DJANGO_QUEUE_MAILER_OFFSET)

        if type(offset) is int:
            offset = datetime.timedelta(hours=offset)

        delete_before = datetime.datetime.utcnow().replace(tzinfo=utc) - offset
        self.filter(sent=True, last_attempt__lte=delete_before).delete()


class Queue(models.Model):
    subject = models.CharField(_('Subject'), max_length=250, blank=True)
    to_address = models.EmailField(_('To'), max_length=250)
    bcc_address = models.EmailField(_('BCC'), max_length=250, blank=True)
    from_address = models.EmailField(_('From'), max_length=250)
    content = models.TextField(_('Content'), blank=True)
    html_content = models.TextField(_('HTML Content'), blank=True)
    app = models.CharField(_('App'), max_length=250, blank=True)
    deferred = models.BooleanField(_('Deferred'), default=False)
    created = models.DateTimeField(_('Created'), auto_now_add=True, editable=False)
    last_attempt = models.DateTimeField(_('Last attempt'), auto_now=False, auto_now_add=False, blank=True, null=True,
                                        editable=False)

    objects = QueueManager()

    class Meta:
        verbose_name = _('Queue')
        verbose_name_plural = _('Queues')

    def add_attachment(self, attachment):
        """
        Takes a Django `File` object and creates an attachment for this mailer message.
        """

        Attachment.objects.create(email=self, file_attachment=attachment)

    def get_backend(self, fail_silently=False, **kwds):
        path = settings.DJANGO_QUEUE_MAILER_EMAIL_BACKEND
        try:
            mod_name, klass_name = path.rsplit('.', 1)
            mod = import_module(mod_name)
        except ImportError as e:
            raise ImproperlyConfigured(('Error importing email backend module %s: "%s"'
                                        % (mod_name, e)))
        try:
            klass = getattr(mod, klass_name)
        except AttributeError:
            raise ImproperlyConfigured(('Module "%s" does not define a '
                                        '"%s" class' % (mod_name, klass_name)))
        return klass(fail_silently=fail_silently, **kwds)

    def send(self):
        if getattr(settings, 'USE_TZ', False):
            # This change breaks SQLite usage.
            self.last_attempt = datetime.datetime.utcnow().replace(tzinfo=utc)
        else:
            self.last_attempt = datetime.datetime.now()

        from_email = self.from_address
        to = explode_addresses(self.to_address)
        subject = self.subject
        text_content = self.content
        message_id = make_msgid()
        message = EmailMultiAlternatives(subject, text_content, from_email, to, headers={'message-id': message_id})
        if self.html_content:
            html_content = self.html_content
            message.attach_alternative(html_content, "text/html")
        if self.bcc_address:
            message.bcc = explode_addresses(self.bcc_address)

        # Add any additional attachments
        for attachment in self.attachment_set.all():
            message.attach_file(os.path.join(settings.MEDIA_ROOT, attachment.file_attachment.name))

        try:
            sent = self.get_backend(fail_silently=False).send_messages([message])

            log = Log()
            log.message_id = message_id
            log.subject = self.subject
            log.to_address = self.to_address
            log.bcc_address = self.bcc_address
            log.from_address = self.from_address
            log.content = self.content
            log.html_content = self.html_content
            log.app = self.app
            log.save()

            self.delete()

        except Exception as e:
            logger.error('Mail Queue Exception: {0}'.format(e))


class Attachment(models.Model):
    file_attachment = models.FileField(upload_to='mail-queue/attachments', blank=True, null=True)
    email = models.ForeignKey(Queue, blank=True, null=True)

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __str__(self):
        return self.file_attachment.name


class Log(models.Model):
    message_id = models.CharField(_('Message-ID'), max_length=250)
    subject = models.CharField(_('Subject'), max_length=250, blank=True)
    to_address = models.EmailField(_('To'), max_length=250)
    bcc_address = models.EmailField(_('BCC'), max_length=250, blank=True)
    from_address = models.EmailField(_('From'), max_length=250)
    content = models.TextField(_('Content'), blank=True)
    html_content = models.TextField(_('HTML Content'), blank=True)
    app = models.CharField(_('App'), max_length=250, blank=True)
    sent = models.DateTimeField(_('Sent'), auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')

    def __str__(self):
        return self.message_id
