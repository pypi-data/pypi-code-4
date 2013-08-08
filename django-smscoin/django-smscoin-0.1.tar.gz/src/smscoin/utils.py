### -*- coding: utf-8 -*- ####################################################

from django.utils.translation import get_language

from django_countries.countries import COUNTRIES

#Countries are stored by language to make them language independant.
_countries_cache = {}


def get_sorted_countries():
    """Return countries sorted by name and translates to current language"""
    language = get_language()
    countries = _countries_cache.get(language, None)
    if countries is None:
        countries = _countries_cache[language] = sorted(COUNTRIES, key=lambda c: c[1])
    
    return countries
