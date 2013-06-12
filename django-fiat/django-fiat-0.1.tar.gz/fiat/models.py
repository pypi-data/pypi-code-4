# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from enumerify import fields

from .enums import SymbolPosition, CurrencyMode, CountryTaxMode
from .signals import slugger

'''
PRE CONDITIONS

* A country can be part of several regions.

    EXAMPLES

    Region: Scandinavia
    Countries: Sweden, Denmark, Norway ...

    Region: Europe
    Countries: Sweden, Denmark, Norway, Finland, Germany, Switzerland ...

    Region: South-East Asia
    Countries: Bangladesh, India, Nepal, Pakistan, Sri Lanka ...

    Region: BRIC
    Countries: Brazil, Russia, India, China

* A country must have one and only one currency

    PROS
    + Does prevent price manipulation

    CONS
    - Does not allow flexibility

* A currency ie EUR (EURO) could be the currency for several countries

    * Foreign-key from Currency to Country
    * A Currency can have several countries tied to it since both Germany and Finland can have the Euro
    * A Country must have a Currency
'''

class Currency(models.Model):
    '''
        DESCRIPTION
        The purpose of this model is to give the developer an easy way to represent Currencies.

        PRE-CONDITIONS
        * A Currency can be set to many countries
        * A Country can and must have one and only one Currency
    '''
    title = models.CharField(max_length=50, verbose_name=_('Currency Title'),
        help_text=_('United States Dollar, Great Britain Pound, etc...'))
    code = models.CharField(max_length=3, verbose_name=_('Currency Abbreviation'),
        help_text=_('ISO 4217 Code - USD, GBP, SEK, etc...'))
    code_position = fields.SelectIntegerField(blueprint=SymbolPosition, default=SymbolPosition.SUFFIX,
        verbose_name=_('Code Position'), help_text=_('The position of currency characters. (Prefix/Suffix)'))
    symbol = models.CharField(max_length=5, blank=True, verbose_name=_('Currency Sign'),
        help_text=_('$, £, kr, etc...'))
    symbol_position = fields.SelectIntegerField(blueprint=SymbolPosition, default=SymbolPosition.SUFFIX,
        verbose_name=_('Sign Position'), help_text=_('The position of currency characters. (Prefix/Suffix)'))
    short = models.CharField(max_length=5, blank=True, verbose_name=_('Symbol'),
        help_text=_('For instance :-, ;- ...'))
    short_position = fields.SelectIntegerField(blueprint=SymbolPosition, default=SymbolPosition.SUFFIX,
        verbose_name=_('Symbol Position'), help_text=_('The position of currency characters. (Prefix/Suffix)'))
    mode = fields.SelectIntegerField(blueprint=CurrencyMode, default=CurrencyMode.CODE, verbose_name=_('Mode'),
        help_text='How the currency is presented. (Code/Sign/Symbol)')

    class Meta:
        ordering = ('code',)
        verbose_name_plural = 'Currencies'

    def __unicode__(self):
        return u"ID: %s, Title: %s, Code: %s" % (self.id, self.title, self.code)

    def get_iso_4217(self):
        return self.code

    def get_by_mode(self):
        if self.mode == CurrencyMode.CODE:
            return self.code
        elif self.mode == CurrencyMode.SIGN:
            return self.sign
        elif self.mode == CurrencyMode.SYMBOL:
            return self.symbol
        else:
            return self.code


class Country(models.Model):
    '''
        DESCRIPTION
        This model is simple data container for data regarding a country

        PRE-CONDITIONS
        * A Currency can be set to many countries - you do not have to be redundant
        * A Country can and must have only one Currency - you do not need to worry about price fiddling customers
    '''
    currency = models.ForeignKey(Currency)
    title = models.CharField(max_length=50, unique=True, verbose_name=_('Title'),
        help_text=_('The country name. E.g. Sweden, Denmark, etc...'))
    slug = models.SlugField()
    code = models.CharField(max_length=2, unique=True, verbose_name=_('Country Code'),
        help_text=_('Two character code. E.g. SE for Sweden. Visit http://www.iptoc.nl.ae/ for more info.'))
    abbreviation = models.CharField(max_length=3, unique=True, verbose_name=_('Country Abbreviation'),
        help_text=_('Three character abbreviation. E.g. SWE for Sweden. Visit http://www.iptoc.nl.ae/ for more info.'))
    locale = models.CharField(max_length=10, verbose_name=_('Locale'),
        help_text=_('Which primary locale to use. E.g. sv-SE, da-DK, etc...'))
    vat_rate = models.DecimalField(max_digits=6, decimal_places=3, default=0, verbose_name=_('VAT Rate'),
        help_text=_('Standard VAT Rate. Should be entered in form 0.25 which means 25%.'))
    tax_mode = fields.SelectIntegerField(blueprint=CountryTaxMode, default=CountryTaxMode.INCLUSIVE)
    is_primary = models.BooleanField(verbose_name=_('Is Primary'),
        help_text=_('The country that was ticked last will be the default catch all country.'))

    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'Countries'

    def __unicode__(self):
        return u"Title: %s, Locale: %s" % (self.title, self.locale)

    def has_vat(self):
        return self.vat_rate > 0

    def get_currency(self):
        return self.currency_set.all().order_by('-priority')[0]

    def get_iso_4217(self):
        return self.currency.get_iso_4217()

    def get_suburbs(self):
        return self.regioncollection_set.filter(region__kind=RegionKind.SUBURB)

    def get_cities(self):
        return self.regioncollection_set.filter(region__kind=RegionKind.CITY)

    def save(self, *args, **kwargs):
        primary_countries = Country.objects.filter(is_primary=True)
        if primary_countries.exists() and self.is_primary:
            # Unmark other countries that is marked is_primary
            for country in primary_countries.filter(is_primary=True):
                country.is_primary = False
                country.save()
        if not Country.objects.all().exists():
            self.is_primary = True
        super(Country, self).save(*args, **kwargs)


class Region(models.Model):
    title = models.CharField(max_length=100, unique=True)
    countries = models.ManyToManyField(Country, through='CountryGroup')

    def __unicode__(self):
        return u"Title: %s" % self.title


class CountryGroup(models.Model):
    '''
        The purpose of this model is to be able to group Country objects
        with Regions when you need to connect a Country instance to a Region.

        You only to create a relation if and only if you have a specific
        need to access a country object thru a Region instance

        Consider the following use case:

        - Region: Europe
            Country: Finland
            Country: Germany
            Country: Norway
            Country: Sweden
            Country: Spain

        - Region: Scandinavia
            Country: Sweden
            Country: Denmark
            Country: Norway

        Lets say that you have two shipping partners in UBS and FedUp

        - UBS ships to all European Countries, UBS is slower but cheaper
        - FedUp only ships to Scandinavia, FedUp is faster but more expensive

        You want to let the customers decide so you allow both shipping methods

        Instead of having to assign a ShippingPrice to each country you can
        assign the shipping prices to each region.
    '''
    region = models.ForeignKey(Region)
    country = models.ForeignKey(Country)

    class Meta:
        unique_together = ('region', 'country')

    def __unicode__(self):
        return u"Region: %s, Country: %s" % (self.region, self.country)


# SIGNALS
pre_save.connect(slugger, sender=Country)