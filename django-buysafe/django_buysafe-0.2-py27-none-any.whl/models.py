from django.db import models
from django.utils.translation import ugettext_lazy as _


class PaymentMethodManager(models.Manager):
    def get_query_set(self):
        qs = super(PaymentMethodManager, self).get_query_set()
        return qs.filter(is_enabled=True)


class PaymentMethod(models.Model):
    TYPE_BUYSAFE = 0
    TYPE_WEBATM = 1
    TYPE_24PAY = 2
    TYPE_PAYCODE = 3
    TYPE_CHOICES = (
        (TYPE_BUYSAFE, _('BuySafe')),
        (TYPE_WEBATM, _('Web ATM')),
        (TYPE_24PAY, _('24Pay')),
        (TYPE_PAYCODE, _('PayCode'))
    )
    name = models.CharField(max_length=100, verbose_name=_('name'))
    payment_type = models.IntegerField(choices=TYPE_CHOICES)
    content = models.TextField(blank=True, verbose_name=_('content'))
    store_id = models.CharField(
        max_length=11, verbose_name=_('SunTech store ID'),
        help_text=_(
            'Should be exactly 10 characters, starting with a capitalized '
            'alphabet.'
        )
    )
    password = models.CharField(
        max_length=20, verbose_name=_('SunTech password'),
        help_text=_(
            'This should usually be the transaction password, which is an '
            'alphanumeric string with length between 8 to 20.'
        )
    )
    is_enabled = models.BooleanField(default=True, verbose_name=_('enabled'))

    enabled = PaymentMethodManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _('Payment method')
        verbose_name_plural = _('Payment methods')
        ordering = ['-is_enabled', 'payment_type', '-id']

    def save(self, *args, **kwargs):
        super(PaymentMethod, self).save(*args, **kwargs)
        if self.is_enabled:
            (PaymentMethod.objects.exclude(id=self.id)
                          .filter(payment_type=self.payment_type,
                                  is_enabled=True)
                          .update(is_enabled=False))

    def __unicode__(self):
        return self.name
