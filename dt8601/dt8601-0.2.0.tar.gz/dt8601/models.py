# -*- coding: utf-8 -*-

"""
dt8601.models
=============

This module contains the primary objects IsoDate and IsoYear
"""

from . import datecore
from . import definitions


class IsoDate(object):

    def __init__(self, year, month=1, day=1, country='DE', state=None):
        """
        init for the IsoDate object

        :param year: year between definitions.MINYEAR and definitions.MAXYEAR
        :param month: month from 1..12
        :param day: day form 1..DAYS_IN_MONTH of year
        :param country: country used for holidays
        :param state: state used for holidays (optional, defaults to None)
        """
        self.year = year
        self.month = month
        self.day = day
        self.country = country
        self.state = state
        self.day_list = datecore.load_year(self.year, self.country, self.state)
        self.julian = datecore.gregorian_to_julian(self.year, self.month, self.day)


    @classmethod
    def parse_iso_string(cls, iso_string, separator='T'):
        """
        parse an ISO8601 string and return a dictionary with the results

        :param iso_string: ISO8601 compliant string (may include time part)
        :param separator:  default to 'T' as set forth in ISO8601, use ' ' for some applications
        :return: a dictionary with the parsing results
        """
        res = datecore.iso8601_parser(iso_string, separator)
        return res


    @classmethod
    def from_iso_string(cls, iso_string, country='DE', state=None, separator='T'):
        """
        initialize an IsoDate instance from an ISO string

        :param iso_string: ISO8601 compliant string (may include time part)
        :param country: country to use as locale for the IsoDate
        :param state: state to use as locale for the IsoDate
        :return: IsoDate instance according to data from the ISO string
        :raise: ValueError if any of the elements have invalid values
        """
        res = datecore.iso8601_parser(iso_string, separator)
        if res['dateformat'] == 'YYYY':
            return cls(year=res['year'], country=country, state=state)
        elif res['dateformat'] == 'YYYY-MM':
            return cls(year=res['year'], month=res['month'], country=country, state=state)
        elif res['dateformat'] == 'YYYY-DDD':
            yr, mo, dy = datecore.doy_to_ymd(res['year'], res['dayofyear'])
            return cls(year=yr, month=mo, day=dy, country=country, state=state)
        elif res['dateformat'] == 'YYYY-WWW':
            yr = res['year']
            wk = res['week']
            yr, mo, dy = datecore.week_to_ymd(yr, wk)
            return cls(year=yr, month=mo, day=dy, country=country, state=state)
        elif res['dateformat'] == 'YYYY-WWW-W':
            yr = res['year']
            wk = res['week']
            wd = res['weekday']
            yr, mo, dy = datecore.week_to_ymd(yr, wk)
            doy = datecore.day_of_year(yr, mo, dy)
            doy += (wd - 1)
            yr, mo, dy = datecore.doy_to_ymd(yr, doy)
            return cls(year=yr, month=mo, day=dy, country=country, state=state)
        elif res['dateformat'] == 'YYYY-MM-DD':
            return cls(year=res['year'], month=res['month'], day=res['day'], country=country, state=state)
        else:
            raise ValueError('invalid iso format')


    @classmethod
    def date_string(cls, year, month, day, isoformat='YYYY-MM-DD', separator='-'):
        """
        return a formatted string in ISO8601 syntax

        :param year: four-digit year
        :param month: month from 1..12
        :param day: day from 1..DAYS_IN_MONTH
        :param isoformat: string with ISO8601 date format
        :param separator: separator for elements, defaults to '-' according to ISO8601 long form
        :return: string according to the isoformat
        """
        return datecore.iso8601_date_string(year, month, day, isoformat, separator)


    def __repr__(self):
        """
        simplest of ways to represent an instance of IsoDate

        :return: a string with repr
        """
        return '<{3} {0}-{1}-{2}>'.format(self.year, self.month, self.day, self.__class__.__name__)


    def julian_date(self):
        """
        return the corresponding julian date for the IsoDate instance

        :return: number with the julian date
        """
        return self.julian


    def day_of_year(self):
        """
        return the day of the year

        :return: number day in the year from 1..365 (366 for leap years)
        """
        return datecore.day_of_year(self.year, self.month, self.day)


    def day_of_week(self):
        """
        return the weekday number in ISO8601 notation (1..7)

        :return: weekday number from 1 (monday) ... 7 (sunday)
        """
        return datecore.day_of_week(self.year, self.month, self.day, fmt='number')


    def day_of_week_name(self, mode='EN'):
        """
        return the weekday name

        depending on mode, the method return 'MO'..'SU' for mode 'en'
        or 'Mon'...'Sun' for mode 'short' or 'Monday'...'Sunday' for mode 'long'
        and the language will be detemrined by the country attribute of the IsoDate instance
        currently 'DE', 'IT', 'AT', 'US'
        :param mode: 'en' | 'short' | 'long'
        :return: weekday as string
        """
        dow = datecore.week_day_name(self.year, self.month, self.day, self.country, mode)
        if mode == 'en':
            return dow
        elif mode == 'short':
            return definitions.COUNTRYDATA[self.country.lower()]['short_day_names'][dow]
        elif mode == 'long':
            return definitions.COUNTRYDATA[self.country.lower()]['long_day_names'][dow]
        else:
            raise ValueError('Invalid weekday mode (must be "en"|"short"|"long")')


    def week_of_year(self):
        """
        determine the week of the year

        :return: iso calendar week (1..52 or 53 for leap years)
        """
        return datecore.week_of_year(self.year, self.month, self.day)


    def day_type(self):
        """
        type of day

        :return: 'workday' | 'holiday' | 'weekend'
        """
        doy = datecore.day_of_year(self.year, self.month, self.day)
        _day = self.day_list[doy]
        if _day == '':
            return 'workday'
        elif _day == 'H':
            return 'holiday'
        elif _day == 'W':
            return 'weekend'
        else:
            return 'unknown'


    def iso_string(self, isoformat, separator='-'):
        """
        return a formatted string in ISO8601 syntax

        :return: ISO8601 long form (with separators) string according to the isoformat
        """
        if isoformat == 'YYYY':
            result = '{yr:04d}'.format(yr=self.year)
        elif isoformat == 'YYYY-MM':
            result = '{yr:04d}{sep}{mo:02d}'.format(yr=self.year, mo=self.month, sep=separator)
        elif isoformat == 'YYYY-MM-DD':
            result = '{yr:04d}{sep}{mo:02d}{sep}{dy:02d}'.format(yr=self.year, mo=self.month, dy=self.day, sep=separator)
        elif isoformat == 'YYYY-WWW':
            result = '{yr:04d}{sep}W{wk:02d}'.format(yr=self.year, wk=self.week_of_year(), sep=separator)
        elif isoformat == 'YYYY-WWW-D':
            result = '{yr:04d}{sep}W{wk:02d}{sep}{wday:1d}'.format(yr=self.year, wk=self.week_of_year(), wday=self.day_of_week(), sep=separator)
        elif isoformat == 'YYYY-DDD':
            result = '{yr:04d}{sep}{doy:03d}'.format(yr=self.year, doy=self.day_of_year(), sep=separator)
        else:
            raise ValueError('invalid iso format')
        return result


    def days_since(self, start_date):
        """
        days since a second IsoDate instance
        """
        return self.julian - start_date.julian_date


    def days_until(self, target_date):
        """
        days until a second IsoDate instance
        """
        return target_date.julian_date - self.julian


    def day_of_year(self):
        """
        return day of the year
        """
        return datecore.day_of_year(self.year, self.month, self.day)


    def day_of_week(self):
        """
        return the day of the week as number from 1..7 (ISO) or as string when using fmt='string'
        """
        return datecore.day_of_week(self.year, self.month, self.day, fmt='number')


    def add_days(self, number_of_days):
        """
        add a number of days and return a new instance of IsoDate (days may be negative)
        """
        the_date = datecore.julian_to_gregorian(int(self.julian) + int(number_of_days))
        return IsoDate(the_date[0], the_date[1], the_date[2])


    def add_workdays(self, number_of_days):
        """
        add a number of work day and return a new instance of IsoDate (days must be positive)
        """
        count = 0
        doy = datecore.day_of_year(self.year, self.month, self.day)
        year = self.year
        holidays = datecore.load_year(year,self.country, self.state)
        while count < number_of_days:
            if doy < datecore.days_in_year(self.year):
                doy += 1
            else:
                year += 1
                doy = 1
                holidays = datecore.load_year(year,self.country, self.state)
            if holidays[doy] == '':
                count += 1
        the_date = datecore.doy_to_ymd(year, doy)
        return IsoDate(the_date[0], the_date[1], the_date[2], self.country, self.state)


    def replace(self, year=None, month=None, day=None):
        """
        replace certain parts of the date and return a new IsoDate instance
        """
        _y = self.year
        _m = self.month
        _d = self.day

        if year is not None:
            _y = year
        if month is not None:
            _m = month
        if day is not None:
            _d = day

        return IsoDate(_y, _m, _d, self.country, self.state)


    def project(self, days=None, hoursperday=8, workhours=8, workdaysonly=True):
        """
        try to mimic a very simple time estimation model

        :param days: number of days of effort
        :param hoursperday: number of hours per workday to use for the projection
        :param workhours: number of working hours per day (should be less than 24 <g>)
        :param workdaysonly: use only workdays for the projection
        :return: a new IsoDate instance with the calculated end date
        """
        effort = days * (hoursperday / workhours)
        count = 0
        doy = datecore.day_of_year(self.year, self.month, self.day)
        year = self.year
        holidays = datecore.load_year(year,self.country, self.state)
        while count < effort:
            if doy < datecore.days_in_year(self.year):
                doy += 1
            else:
                year += 1
                doy = 1
                holidays = datecore.load_year(year,self.country, self.state)
            if workdaysonly is True:
                if holidays[doy] == '':
                    count += 1
            else:
                count += 1
        the_date = datecore.doy_to_ymd(year, doy)
        return IsoDate(the_date[0], the_date[1], the_date[2], self.country, self.state)


    def __str__(self):
        """
        return string representation for the instance

        :return: string with formatted date
        """
        return self.iso_string('YYYY-MM-DD')


class IsoYear(object):

    def __init__(self, year=None, country='DE', state=None):
        """
        constructor for the IsoYear
        :param year: the year
        :param country: defaults to DE
        :param state: state (bundesland)
        :raise: ValueError if year not in MINYEAR..MAXYEAR
        """
        if not definitions.MIN_YEAR < year < definitions.MAX_YEAR:
            raise ValueError('Year has to be between {0} and {1}'.format(definitions.MIN_YEAR, definitions.MAX_YEAR))

        self.year = year
        self.country = country
        self.state = state
        if self.country is not None:
            self.country = self.country.upper()
        if self.state is not None:
            self.state = self.state.upper()
        self.holiday_list = datecore.calc_holidays(self.year, self.country, self.state)
        self.day_list = datecore.load_year(self.year, self.country, self.state)


    def __repr__(self):
        return '<IsoYear {0}>'.format(self.year)

    @property
    def week_count(self):
        """
        return the number of weeks for this year

        :return: integer 52 or 53
        """
        return datecore.weeks_in_year(self.year)

    @property
    def leap_year(self):
        """
        check if a year is a leap year

        :return: boolean True or False
        """
        return datecore.is_leap_year(self.year)

    @property
    def iso_weeks(self):
        """
        get the list of all iso calendar weeks for the year

        this property yields the list of calendar weeks (ISO weeks starting with a monday (weekday number 1)
        for the year. Each entry is a dictionary with the key 'no' holing the week no,
        the key 'start' containing a tuple of (year, month, day).
        As ISO weeks starts on a monday, the weekday of every date is always a monday.

        :return: array of 52 or 52 tuples
        """
        week_list = []
        for w in xrange(1, datecore.weeks_in_year(self.year) + 1):
            ymd = datecore.week_to_ymd(self.year, w)
            week_list.append({'no': w, 'start': (ymd[0], ymd[1], ymd[2])})
        return week_list


    @property
    def holidays(self):
        """
        return the list of holidays for the year

        :return: list of holiday entries
        """
        return self.holiday_list

    @property
    def easter(self):
        """
        helper property to get the date tuple (year, month, day) for easter sunday

        :return: date tuple for easter sunday
        """
        return datecore.easter_sunday(self.year)

    def is_holiday(self, month, day):
        """
        check if a given day in a given month is a holiday or a weekend day
        :param month: integer from 1..12 for the month
        :param day:  integer from 1..DAYS_IN_MONTH for the day
        :return: True if the day is a holiday
        """
        doy = datecore.day_of_year(self.year, month, day)
        _day = self.day_list[doy]
        return _day != ''

    def workdays_in_month(self, month):
        """
        return the number of working days in the given month
        :param month: integer 1..12
        :return: int with the number of workdays
        """
        work_days = 0
        doy = datecore.day_of_year(self.year, month, 1)
        count = datecore.days_in_month(self.year, month)
        for i in self.day_list[doy:doy + count]:
            if i == '':
                work_days += 1
        return work_days

    def ultimo(self, month):
        """
        returns the ultimo (last workday of the month) for a given month
        :param month: the month from 1..12
        :return: a new instance of IsoDate with the ultimo for the month
        """
        res = datecore.ultimo(self.year, month)
        while self.is_holiday(res[1], res[2]) or datecore.day_of_week(res[0], res[1], res[2]) in ['SA', 'SU']:
            res = datecore.add_days(res[0], res[1], res[2], -1)
        return IsoDate(res[0], res[1], res[2], self.country, self.state)

    def primo(self, month):
        """
        returns the primo (first workday of the month) for a given month
        :param month: the month from 1..12
        :return: a new instance of IsoDate with the primo for the month
        """
        res = (self.year, month, 1)
        while self.is_holiday(res[1], res[2]) or datecore.day_of_week(res[0], res[1], res[2]) in ['SA', 'SU']:
            res = datecore.add_days(res[0], res[1], res[2], +1)
        return IsoDate(res[0], res[1], res[2], self.country, self.state)

    def get_month_name(self, the_month, mode='short'):
        """
        just a helper method to get the month name according to the country attribute of the IsoYear instance
        :param the_month: the month from 1..12
        :param mode: 'short' | 'long'
        :return: string with the month name
        """
        if mode == 'short':
            return definitions.COUNTRYDATA[self.country]['short_month_names'][the_month]
        elif mode == 'long':
            return definitions.COUNTRYDATA[self.country]['long_month_names'][the_month]
        else:
            return the_month


