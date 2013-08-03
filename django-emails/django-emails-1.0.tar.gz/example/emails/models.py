from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import dateformat
from django.conf import settings
    
    
PRIORITIES = (
    (1, "high"),
    (2, "medium"),
    (3, "low"),
)

TYPE = (
    ('plain', "Text"),
    ('html', "HTML")
)

class Message(models.Model):
    sender_address = models.EmailField(_('Sender E-mail'), blank=False, null=False)
    subject = models.CharField(_('Subject'), max_length=255, blank=False, null=False)
    content = models.TextField(_('Content'), blank=False, null=False)
    timestamp = models.DateTimeField(_('Date and time'), auto_now = True, blank=False, null=False)
    priority = models.PositiveIntegerField(choices=PRIORITIES, default=2, blank=False, null=False)
    type = models.CharField(_('Type'), choices=TYPE, max_length=5, default='text', blank=False, null=False)
    
    def __unicode__(self):
        return dateformat.format(self.timestamp, settings.DATETIME_FORMAT) 
    
    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')

    
class Recipient(models.Model):
    address = models.EmailField(_('E-mail'))
    message = models.ForeignKey(Message)
    sent = models.BooleanField(_('Is sent'), default=False)
    
    def __unicode__(self):
        return self.address
    
    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')
