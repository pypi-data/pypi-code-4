# -*- coding: utf-8 -*-
# Copyright (c) 2004-2012 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from datetime import datetime
import time

from zope.i18n.locales import locales, LoadLocaleError
from zope.i18n.interfaces import IUserPreferredLanguages

_marker = object()


def get_locale_info(request):
    if request == _marker:
        return 'en'
    languages = IUserPreferredLanguages(request).getPreferredLanguages()
    return (languages and languages[0]) or 'en'


def get_locale_dates(request=_marker, locale=_marker):
    """Return the date formatter given the request.
    """
    local_info = locale
    if local_info is _marker:
        local_info = get_locale_info(request)
    try:
        return locales.getLocale(*local_info.split('-')).dates
    except LoadLocaleError:
        return locales.getLocale('en').dates


def get_formatted_now(request):
    """Return the current date formatted given the request local
    """
    now = time.gmtime()
    formatter = get_locale_dates(request).getFormatter('dateTime', 'full')
    return formatter.format(datetime(*now[:6]))


def get_formatted_date(
    date, size="full", request=_marker, locale=_marker, display_time=True):
    """Return a formatted date given the locale or request.

       date should be a tuple (year, month, day[, hour[, minute[,
       second]]]) or a datetime instance.
    """
    if not isinstance(date, datetime):
        date = datetime(*date)
    format = 'dateTime' if display_time else 'date'
    formatter = get_locale_dates(request, locale).getFormatter(format, size)
    return formatter.format(date)


def get_month_names(
    request=_marker, locale=_marker, calendar='gregorian'):
    """returns a list of month names for the current locale
    """
    dates = get_locale_dates(request, locale)
    return dates.calendars[calendar].getMonthNames()


def get_month_abbreviations(
    request=_marker, locale=_marker, calendar='gregorian'):
    """returns a list of abbreviated month names for the current locale
    """
    dates = get_locale_dates(request, locale)
    return dates.calendars[calendar].getMonthAbbreviations()


# BBB
getlocaleinfo = lambda self: get_locale_info(self.REQUEST)
getFormattedNow = lambda self, *args, **kwargs: get_formatted_now(
    self.REQUEST, *args, **kwargs)
getFormattedDate = lambda self, *args, **kwargs: get_formatted_date(
    self.REQUEST, *args, **kwargs)
getMonthNames = lambda self, *args, **kwargs: get_month_names(
    self.REQUEST, *args, **kwargs)
getMonthAbbreviations = lambda self, *args, **kwargs: get_month_abbreviations(
    self.REQUEST, *args, **kwargs)
