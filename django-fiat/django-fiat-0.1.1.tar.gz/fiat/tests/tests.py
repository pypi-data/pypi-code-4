# -*- coding: utf-8 -*-

from django.test import TestCase

from django.db import IntegrityError

from fiat.models import Currency, Country, Region, CountryGroup

class RegionTest(TestCase):
    def setUp(self):
        # Create Currency instance Sweden
        self.currency =  Currency.objects.create(
            title=u'United States Dollar',
            code=u'USD',
            sign=u'$',
        )
        # Create Country instance Sweden
        self.country = Country.objects.create(
            currency=self.currency,
            title=u'United States',
            # slug=u'sweden',
            code=u'US',
            abbreviation=u'USA',
            locale=u'en-US',
        )

    def test_title(self):
        self.assertEqual(self.country.title, u'United States')

    def test_autoslug(self):
        self.assertEqual(self.country.slug, 'united-states')

    def test_title_unique_or_fail(self):
        with self.assertRaises(IntegrityError):
            Country.objects.create(
                currency=self.currency,
                title=u'United States',
                code=u'SU',
                abbreviation=u'ASU',
                locale=u'en-US',
            )

    def test_code_unique_or_fail(self):
        with self.assertRaises(IntegrityError):
            Country.objects.create(
                currency=self.currency,
                title=u'United Estates',
                code=u'US',
                abbreviation=u'ASU',
                locale=u'en-US',
            )

    def test_abbreviation_unique_or_fail(self):
        with self.assertRaises(IntegrityError):
            Country.objects.create(
                currency=self.currency,
                title=u'United Estates',
                code=u'SU',
                abbreviation=u'USA',
                locale=u'en-US',
            )

    def test_duplicate_slug_appends_no(self):
        # Set code=YS, abbreviation=YSA in order for us to not get an IntegrityError
        country = Country.objects.create(
            currency=self.currency,
            title=u'United states',
            code=u'YS',
            abbreviation=u'YSA',
            locale=u'en-US'
        )
        self.assertEqual(country.slug, 'united-states-1')

    def test_country_code(self):
        self.assertEqual(self.country.code, 'US')

    def test_is_primary(self):
        country = Country.objects.get(code='US')
        self.assertTrue(country.is_primary)

    def test_set_denmark_as_primary(self):
        euro = Currency.objects.create(
            title=u'Euro',
            code=u'EUR',
            sign=u'€',
        )
        denmark = Country.objects.create(
            currency=euro,
            title=u'Denmark',
            slug='denmark',
            code=u'DK',
            abbreviation=u'DKK',
            locale=u'da-DK',
            is_primary=True
        )
        self.assertTrue(denmark.is_primary)
        # US no longer primary
        country = Country.objects.get(code='US')
        self.assertFalse(country.is_primary)

    def test_currency_code(self):
        ''' Test that the danish currency code returns EUR '''
        country = Country.objects.get(code='US')
        self.assertEqual(country.get_iso_4217(), 'USD')

    def test_danish_currency(self):
        ''' Test that the danish currency code returns EUR '''
        euro = Currency.objects.create(
            title=u'Euro',
            code=u'EUR',
            sign=u'€',
        )
        denmark = Country.objects.create(
            currency=euro,
            title=u'Denmark',
            slug='denmark',
            code=u'DK',
            abbreviation=u'DKK',
            locale=u'da-DK',
            is_primary=True
        )
        self.assertEqual(denmark.get_iso_4217(), 'EUR')

    def test_european_countries(self):
        ''' Add countries to a region '''
        europe = Region.objects.create(title=u'Europe')
        euro = Currency.objects.create(title=u'Euro', code=u'EUR', sign=u'€')
        denmark = Country.objects.create(
            currency=euro,
            title=u'Denmark',
            slug='denmark',
            code=u'DK',
            abbreviation=u'DKK',
            locale=u'da-DK',
        )
        nok = Currency.objects.create(title=u'Norwegian Krona', code=u'NOK', sign=u';-')
        norway = Country.objects.create(
            currency=nok,
            title=u'Norway',
            slug='norway',
            code=u'NO',
            abbreviation=u'NOK',
            locale=u'no-NO',
        )
        CountryGroup.objects.create(region=europe, country=norway)
        CountryGroup.objects.create(region=europe, country=denmark)
        self.assertEqual(europe.countries.count(), 2)