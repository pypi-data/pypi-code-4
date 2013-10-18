from django.utils.translation import ugettext as _
from django.db import models


class EmailTemplate(models.Model):
    name = models.CharField(_('Template name'), max_length=100, unique=True)
    subject = models.CharField(_('Subject'), max_length=254)
    text_message = models.TextField(_('Text message'), null=True, blank=True)
    html_message = models.TextField(_('HTML message'), null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Email template')
        verbose_name_plural = _('Email templates')
