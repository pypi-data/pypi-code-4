from django.db import models
from django.utils.translation import ugettext_lazy as _
from emails.signals import send_notification, send_field_notification

# Create your models here.

class Example(models.Model):
    email = models.EmailField(_('Email'))
    text = models.TextField(_('Text'))
    boolean = models.BooleanField(_('Boolean'))
    
    def __unicode__(self):
        return self.email
    
    class Meta:
        verbose_name = _('Example')
        verbose_name_plural = _('Example')
        
send_notification.register(sender = Example, notification_fields = ['email', 'text', 'boolean'])
send_field_notification.register(sender = Example, email_field = 'email', subject = 'Test field notification', 
                                 template = 'emails/test2.html')
    
    