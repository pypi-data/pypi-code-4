### -*- coding: utf-8 -*- ####################################################

from decimal import Decimal, ROUND_DOWN

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from django_countries.fields import CountryField
from django_countries.countries import COUNTRIES

COUNTRY_DICT = dict(COUNTRIES)

#Countries are stored by language to make them language independant.
_countries_cache = {}


class Provider(models.Model):
    """
    Model for providers
        - **country** -- provider's country
        - **code** -- unique code 
        - **name** -- provider's name
        - **number** -- number
        - **prefix** -- each message must contain this prefix
        - **rewrite** -- rewrite prefix
        - **price** -- price in default currency
        - **currency** -- currency in which the calculation is performed
        - **usd** -- price in US dollars
        - **profit** -- profit in percents
        - **vat** -- Value added tax
        - **notice** -- some notice about provider
        - **modified** -- date of creating or editing information
    """

    country = CountryField(_("Country"))
    code = models.CharField(_("Code"), max_length=64, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=64, blank=True, null=True)
    number = models.CharField(_("Number"), max_length=15)
    prefix = models.CharField(_("Prefix"), max_length=16)
    rewrite = models.CharField(_("Rewrite prefix"), max_length=16, blank=True, null=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=64)
    usd = models.DecimalField(_("Price in US dollars"), max_digits=10, decimal_places=2)
    profit = models.DecimalField(_("Profit in percents"), max_digits=10, decimal_places=2)
    vat = models.BooleanField(_("VAT"), default=False)
    notice = models.CharField(_("Notice"), max_length=512, blank=True)
    
    modified = models.DateTimeField(_('modified date/time'), blank=True, null=True, editable=False)
    
    class Meta:
        ordering = ('country', 'code',)
        verbose_name = _("provider")
        verbose_name_plural = _("providers")
    
    @classmethod
    def get_sorted_countries(cls):
        """Method returns countries sorted by name and translates to current language"""
        countries = ((code, force_unicode(COUNTRY_DICT[code])) for code in cls.objects.distinct().values_list('country', flat=True).order_by('country') if code in COUNTRY_DICT)
        countries = sorted(countries, key=lambda c: c[1])
        
        return countries
    
    def get_profit_str(self):
        """String representation of profit"""
        return str((self.usd*self.profit/Decimal('100.0')).quantize(Decimal('.01'), rounding=ROUND_DOWN))
    