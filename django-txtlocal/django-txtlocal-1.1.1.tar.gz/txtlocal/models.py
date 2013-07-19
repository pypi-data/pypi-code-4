from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class InboxSMS(models.Model):
    """A message recieved from txtlocal."""
    sender = models.CharField(_('The mobile number of the sender.'), max_length=20)
    content = models.CharField(_('The message content.'), max_length=255, default='', blank=True)
    in_number = models.CharField(_('The number the message was sent to (your inbound number).'), max_length=20, default='', blank=True)
    email = models.EmailField(_('Any email address extracted.'), max_length=255, default='', blank=True)
    credits = models.IntegerField(_('The number of credits remaining on your Txtlocal account.'), null=True, blank=True)
    time = models.DateTimeField(_('Date and time when parameters were received'), default=timezone.now)

    def __unicode__(self):
        return u"%s" % (self.content)

    class Meta:
        verbose_name_plural = _('Inbox SMS')
