# -*- coding: utf-8 -*-

"""
dt8601.datecore
===============

This module provides utility functions that are also useful for external consumption.
"""

from . import definitions
import re


def is_number(s):
    try:
        if s is not None:
            float(s)
            return True
        else:
            return False
    except ValueError, TypeError:
        return False


def gregorian_to_julian(year, month, day):
    """
    convert ymd tuple to julian day number

    :param year: four digit year from MINYEAR..MAXYEAR
    :param month: month from 1..12
    :param day: day from 1..DAYS_IN_MONTH
    """
    JD0 = 1721426
    LT = day_of_year(year, month, day) - 1
    LJ = year - 1
    N400 = LJ / 400
    R400 = LJ % 400
    N100 = R400 / 100
    R100 = R400 % 100
    N4 = R100 / 4
    N1 = R100 % 4
    JD = JD0 + N400 * 146097 + N100 * 36524 + N4 * 1461 + N1 * 365 + LT
    return JD


def julian_to_gregorian(julian_number):
    """
    convert julian date number to ymd tuple
    :param julian_number: the julian date to convert
    """
    JD = julian_number
    JD0 = 1721426
    N400 = (JD - JD0) / 146097
    R400 = (JD - JD0) % 146097
    N100 = R400 / 36524
    R100 = R400 % 36524
    if N100 == 4:
        N100 = 3
        R100 = 36524
    N4 = R100 / 1461
    R4 = R100 % 1461
    N1 = R4 / 365
    LT = R4 % 365
    if N1 == 4:
        N1 = 3
        LT = 365
    LJ = 400 * N400 + 100 * N100 + 4 * N4 + N1
    J = LJ + 1
    return doy_to_ymd(J, LT + 1)


def julian_to_mjd(julian_number):
    """
    convert julian date to modified julian date
    """
    return julian_number - 2400000.5


def mjd_to_julian(mjd_number):
    """
    convert modified julian date to julian date
    """
    return mjd_number + 2400000.5


def easter_schlyter(year):
    """
    calculate schöyter easter sunday day number

    :param year: the four digit year
    """
    a = year % 19
    b = year / 100
    c = year % 100
    d = b / 4
    e = b % 4
    f = (b + 8) / 25
    g = (b - f + 1) / 3
    h = (19 * a + b - d - g + 15) % 30
    i = c / 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) / 451
    return h + l - 7 * m + 22


def easter_sunday(year):
    """
    calculate easter sunday for a given year

    :param year: four-digit year
    :returns: ymd tuple for easter sunday
    """
    day = easter_schlyter(year)
    month = 3
    if day > 31:
        month = 4
        day -= 31
    return year, month, day


def is_leap_year(year):
    """
    check if year is a leap year

    :param year: four digit year
    :returns: True or False
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def days_in_month(year, month):
    """
    calculate the number of days in a given month

    :param year: four digit year
    :param month: month from 1..12
    :returns: integer with days in month
    """
    ultimo_day = definitions.DAYS_IN_MONTH[month]
    if ultimo_day == 28 and is_leap_year(year):
        ultimo_day += 1
    return ultimo_day


def day_of_year(year, month, day):
    """
    calculate the day number within a year (1..365/366)

    :param year: four-digit year
    :param month: month from 1..12
    :param day: day from 1..DAYS_IN_MONTH
    """
    days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    doy = 0
    if month > 1:
        doy = days[month - 1]
        if is_leap_year(year) and month > 2:
            doy += 1
    doy += day
    return doy


def days_in_year(year):
    """
    helper method to get the number of days in a year

    :param year: four digit year
    :returns: 365 or 366
    """
    if is_leap_year(year):
        return 366
    else:
        return 365


def day_of_week(year, month, day, fmt='string'):
    """
    calculate the day of the week

    day_of_week either returns a number from 1..7 or a string from MO..SU
    depending on the fmt keyword parameter (numbering according to ISO8601)

    :param year: four-digit year
    :param month: month from 1..12
    :param day: day from 1..DAYS_IN_MONTH
    :param fmt: 'number' for 1..7 or 'string' for 'MO'..'SU'
    :returns: weekday as integer or string
    """
    wdays = [None, 'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    t = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    if month < 3:
        year -= 1
    t = (year + year / 4 - year / 100 + year / 400 + t[month - 1] + day) % 7
    if t == 0:
        t = 7
    if fmt == 'number':
        return t
    else:
        return wdays[t]


def week_of_year(year, month, day):
    """
    calculate the ISO week number (1..53) for a given date

    :param year: four-digit year
    :param month: month from 1..12
    :param day: day from 1..DAYS_IN_MONTH
    :returns: integer ISO week number
    """
    doy = day_of_year(year, month, day)
    wday = day_of_week(year, month, day, fmt='number')
    tmp = (doy - wday + 10) / 7
    if tmp == 0:
        tmp = week_of_year(year - 1, 12, 31) * -1
    return tmp


def weeks_in_year(year):
    """
    calculate the number of week in a given year
    :param year: four-digit year
    :returns: integer 1..53
    """
    dayofyear = 1
    while day_of_week(*doy_to_ymd(year, dayofyear), fmt='number') != 4:
        dayofyear += 1
    thursdays = 0
    while dayofyear <= days_in_year(year):
        thursdays += 1
        dayofyear += 7
    return thursdays


def doy_to_ymd(year, dayofyear):
    """
    convert day within a given year to a ymd tuple

    :param dayofyear: 1..365/366
    :param year: four-digit year
    :returns: ymd tuple
    """
    md = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not 1 <= dayofyear <= days_in_year(year):
        raise ValueError('invalid day number')
    if is_leap_year(year):
        md[2] += 1
    index = dayofyear
    m = 1
    while index > md[m]:
        index -= md[m]
        m += 1
    return year, m, index


def week_to_ymd(year, week):
    """
    calculate the beginning of a ISO week number

    :param year: four-digit year
    :param week: ISO week number 1..53
    """
    month = 1
    day = 1
    dayofyear = 1
    wk = week_of_year(year, month, day)
    if wk < 0:
        while day_of_week(*doy_to_ymd(year, dayofyear), fmt='number') != 1:
            dayofyear += 1
        wday = 1
    else:
        wday = day_of_week(*doy_to_ymd(year, dayofyear), fmt='number')
    if week > 1:
        dayofyear += (week-1) * 7
    if wday != 1:
        dayofyear -= wday-1
    if dayofyear < 1:
        dayofyear = days_in_year(year-1) - dayofyear
        year -= 1
    return doy_to_ymd(year, dayofyear)


def add_days(year, month, day, days_to_add):
    """
    add days to a date, days_to_add can be negative also
    :param year: four-digit year
    :param month: month form 1..12
    :param day: day from 1..DAYS_IN_MONTH
    :param days_to_add: integer days to add
    :returns: ymd tuple
    """
    julian = gregorian_to_julian(year, month, day)
    julian += days_to_add
    return julian_to_gregorian(julian)


def load_year(year, country='DE', state=None):
    """
    load the day list (weekend, holiday or normal day) for a given year and a given location

    :param year: four-digit year
    :param country: ISO2 code for the coutry
    :param state: state code (see definitions module)
    :returns: list of day entries for every day of the year (''|'W'|'H')
    """
    weekend = definitions.COUNTRYDATA[country]['weekend']
    year_matrix = ['' for x in range(367)]
    max_feb = 28
    if is_leap_year(year):
        max_feb += 1
    for month in range(1,13):
        if month == 2:
            dim = max_feb
        else:
            dim = definitions.DAYS_IN_MONTH[month]
        for day in range(1, dim + 1):
            dow = day_of_week(year, month, day)
            doy = day_of_year(year, month, day)
            if dow in weekend:
                year_matrix[doy] = 'W'

    holidays = calc_holidays(year, country, state)
    for holiday in holidays:
        name, datelist = holiday
        for the_date in datelist:
            doy = day_of_year(*the_date)
            year_matrix[doy] = 'H'

    return year_matrix


def calc_holidays(year, country='DE', state=None):
    """
    calculate the list of holidays for a year in a location

    :param year: four-digit year
    :param country: ISO2 country code
    :param state: state code (see definitions module)
    :returns: list of holiday tuples (name, date tuple)
    """
    holiday_list = []

    for holiday in definitions.COUNTRYDATA[country]['holidays']:
        use_holiday = True
        if state is not None:
            if ('states' in holiday and state in holiday['states']) or ('states' not in holiday):
                use_holiday = True
            else:
                use_holiday = False
        else:
            if 'states' in holiday:
                use_holiday = False
        if use_holiday:
            holiday_name = holiday["name"]
            holiday_date = parse_holiday(year, holiday["date"])
            if holiday_date is not None:
                holiday_list.append((holiday_name, holiday_date))

    return holiday_list


def parse_holiday(year, holiday_definition):
    """
    parse a holiday definition and return the date

    :param year: four-digit year
    :param holiday_definition: a string with a holidays definition
    """
    fields = holiday_definition.split(':')
    if fields[0] == 'F':
        date_list = parse_fixed_holiday(year, holiday_definition)
    elif fields[0] == 'V':
        date_list = parse_variable_holiday(year, holiday_definition)
    else:
        raise ValueError('holiday type not in "F", "V"')
    return date_list


def parse_fixed_holiday(year, holiday_definition):
    """
    parse a fixed holiday that always occurs on the same month and day

    :param year: four-digit year
    :param holiday_definition: string with the holiday definition
    :returns: tuple with date(s) of the holiday
    """
    fields = holiday_definition.split(':')
    month_day = fields[1].split('-')
    spread = fields[2].split(',') if fields[2] != '' else None
    validity = fields[3].split('-') if fields[3] != '' else None
    the_date = (year, int(month_day[0]), int(month_day[1]))
    valid_year = True  # be optimistic ...

    if validity is not None and not validity[0] <= year <= validity[1]:
        valid_year = False

    if valid_year:
        '''
        we check the spread. for some countries, if the holiday occurs on a wekeend,
        the day off to celeberate the holiday will be a defined weekday.
        For instance, if the Independence Day (July 4th) occurs on a saturday,
        the friday will be a non-working day. If it occurs on a sunday, the non-working day
        will be the following monday. For this reason, we need the ability to have more
        than one entry in our spread.
        '''
        result = [the_date]  # default is the holiday only
        if spread:
            for entry in spread:
                curr = the_date
                week_day = day_of_week(the_date)
                if week_day == entry[0:2].upper():  # we have a match for the day in e.g. "SA-FR"
                    direction = entry[2:3]  # count back or forward
                    target = entry[3:].upper()  # to which target weekday?
                    while day_of_week(curr) != target:  # ok, loop
                        curr = add_days(curr[0], curr[1], curr[2], 1 if direction == '+' else -1)
                else:
                    curr = None  # no match, no additional day for the result
                if curr is not None:
                    result.append(curr)
        return result
    else:
        return None


def calculate_base_date(year, the_base):
    """
    calculate the base date for a variable holiday

    :param year: four-digit year
    :param the_base: string with base: EASTER|ADVENT|JAN...DEC
    :returns: ymd tuple
    """
    the_base = the_base.upper()
    result = None
    if the_base == 'EASTER':
        result = easter_sunday(year)
    elif the_base == 'ADVENT':
        xmas = (year, 12, 24)
        while day_of_week(xmas[0], xmas[1], xmas[2]) != 'SU':
            xmas = add_days(xmas[0], xmas[1], xmas[2], -1)
        result = add_days(xmas[0], xmas[1], xmas[2], -28)
    elif the_base == 'JAN':
        result = (year, 1, 1)
    elif the_base == 'FEB':
        result = (year, 2, 1)
    elif the_base == 'MAR':
        result = (year, 3, 1)
    elif the_base == 'APR':
        result = (year, 4, 1)
    elif the_base == 'MAY':
        result = (year, 5, 1)
    elif the_base == 'JUN':
        result = (year, 6, 1)
    elif the_base == 'JUL':
        result = (year, 7, 1)
    elif the_base == 'AUG':
        result = (year, 8, 1)
    elif the_base == 'SEP':
        result = (year, 9, 1)
    elif the_base == 'OCT':
        result = (year, 10, 1)
    elif the_base == 'NOV':
        result = (year, 11, 1)
    elif the_base == 'DEC':
        result = (year, 12, 1)
    return result


def parse_variable_holiday(year, holiday_definition):
    """
    parse a variable holiday

    :param year: four-digit year
    :param holiday_definition: string with definition for a variable holiday
    :returns: tuple with date(s) of the holiday
    """
    fields = holiday_definition.split(':')
    base = fields[1].upper()
    formula = fields[2]
    spread = fields[3].split(',') if fields[3] != '' else None

    validity = None
    if fields[4] != '':
        validity = fields[4].split('-')
        if validity[0] == '':
            validity[0] = definitions.MIN_YEAR
        else:
            validity[0] = int(validity[0])
        if validity[1] == '':
            validity[1] = definitions.MIN_YEAR
        else:
            validity[1] = int(validity[1])

    base = calculate_base_date(year, base)
    the_date = base

    # process formula here
    token_list = re.findall("[+-][^+-]+", formula)
    for token in token_list:
        if token[1:].isdigit():
            the_date = add_days(the_date[0], the_date[1], the_date[2], int(token))
        else:
            direction = token[0]
            target = token[1:3].upper()
            curr = the_date
            curr = add_days(curr[0], curr[1], curr[2], +1 if direction == '+' else -1)
            while day_of_week(curr[0], curr[1], curr[2]) != target:  # ok, loop
                curr = add_days(curr[0], curr[1], curr[2], 1 if direction == '+' else -1)
            the_date = curr

    valid_year = True  # be optimistic ...

    if validity is not None and not validity[0] <= year <= validity[1]:
        valid_year = False

    if valid_year:
        result = [the_date]
        if spread:
            for entry in spread:
                curr = the_date
                week_day = day_of_week(*the_date)
                if week_day == entry[0:2].upper():  # we have a match for the day in e.g. "SA-FR"
                    direction = entry[2:3]  # count back or forward
                    target = entry[3:].upper()  # to which target weekday?
                    while day_of_week(*curr) != target:  # ok, loop
                        curr = add_days(curr[0], curr[1], curr[2], 1 if direction == '+' else -1)
                else:
                    curr = None  # no match, no additional day for the result
                if curr is not None:
                    result.append(curr)
        return result
    else:
        return None


def get_month_name(month, country='DE', mode='short'):
    """
    retrieve name of the month in various formats

    :param month: month from 1..12
    :param country: ISO2 code for country language
    :param mode: string with 'short' or 'long' (see definitions module)
    :returns: string with the month name
    """
    if mode == 'short':
        return definitions.COUNTRYDATA[country]['short_month_names'][month]
    elif mode == 'long':
        return definitions.COUNTRYDATA[country]['long_month_names'][month]
    else:
        return month


def week_day_name(year, month, day, country='DE', mode='EN'):
    """
    retrieve name of the week day in various formats

    :param year: four-digit year
    :param month: month from 1..12
    :param day: day from 1..DAYS_IN_MONTH
    :param country: ISO2 code for country language
    :param mode: string with 'en' or 'short' or 'long' (see definitions module)
    :returns: string with the month name
    """
    dow = day_of_week(year, month, day, fmt='string')
    if mode == 'en':
        return dow
    elif mode == 'short':
        return definitions.COUNTRYDATA[country.lower()]['short_day_names'][dow]
    elif mode == 'long':
        return definitions.COUNTRYDATA[country.lower()]['long_day_names'][dow]
    else:
        raise ValueError('Invalid weekday mode (must be "en"|"short"|"long")')


def iso8601_parser(input_string, separator='T'):
    """
    main wrapper method for the ISO8601 date/time parser

    :param input_string: ISO8601 date/time string
    :param separator: defaults to 'T' according to ISO8601
    :returns: dictionary with the parsing results
    """
    dt, ti, tz = iso8601_splitter(input_string,separator)
    res = {}
    if dt is not None:
        res.update(iso8601_date_parser(dt))
    if ti is not None:
        res.update(iso8601_time_parser(ti))
    if tz is not None:
        res.update(iso8601_timezone_parser(tz))
    return res


def iso8601_splitter(input_string, separator='T'):
    """
    split an ISO8601 date/time string in date, time, tz parts

    basic logic:
    - if it has a 'T' in it, it is a date and time input
    - if it has ['Z', 'z', '+', '-'] in it, it has a timezone information

    :param input_string: ISO8601 string
    :param separator: default to 'T' according to ISO8601
    :returns: tuple with datepart, timepart, tzpart
    """
    timezone_part = None
    has_time = input_string.upper().find(separator)

    if has_time > -1:
        date_part = input_string[:has_time]
        time_part = input_string[has_time + 1:]

        has_timezone = time_part.upper().find('Z')
        if has_timezone == -1:
            has_timezone = time_part.find('+')
        if has_timezone == -1:
            has_timezone = time_part.find('-')

        if has_timezone > -1:
            timezone_part = time_part[has_timezone:]
            time_part = time_part[:has_timezone]
        else:
            timezone_part = None

    else:
        date_part = input_string
        time_part = None

    return date_part, time_part, timezone_part


def iso8601_date_parser(input_string):
    """
    parse an ISO8601 date string
    :param input_string: ISO8601 date string
    :returns: dictionary with parsing results
    """
    work = input_string.replace('-', '')
    date_length = len(work)

    _y = None
    _m = None
    _d = None
    _w = None
    _wday = None
    _doy = None
    _format = None

    if date_length not in [4, 6, 7, 8]:
        raise ValueError('ISO8601 date length invalid')
    else:
        use_week = False
        if len(work) > 4:
            use_week = work[4] == 'W'

        if not use_week and not is_number(work):
            raise ValueError('ISO8601 date without week reference has to be numeric')

        if date_length == 4:
            _y = int(work)
            _format = 'YYYY'
        elif date_length == 6:
            _y = int(work[0:4])
            _m = int(work[4:6])
            _format = 'YYYY-MM'
        elif date_length == 7:
            if use_week:
                _y = int(work[0:4])
                _w = int(work[5:7])
                _format = 'YYYY-WWW'
            else:
                _y = int(work[0:4])
                _doy = int(work[4:7])
                _format = 'YYYY-DDD'
        elif date_length == 8:
            if use_week:
                _y = int(work[0:4])
                _w = int(work[5:7])
                _wday = int(work[7:8])
                _format = 'YYYY-WWW-W'
            else:
                _y = int(work[0:4])
                _m = int(work[4:6])
                _d = int(work[6:8])
                _format = 'YYYY-MM-DD'

    return {'year': _y, 'month': _m, 'day': _d, 'week': _w, 'weekday': _wday,
            'dayofyear': _doy, 'iso_date': work, 'dateformat': _format}


def is_valid_time(hours, minutes, seconds):
    """
    check if a time is valid (within 00:00:00 to 24:00:00)

    :param hours: hour from 00..24 (yes, 24 is valid for 24:00:00)
    :param minutes: minutes form 00..59
    :param seconds: seconds from 00..60 (yes, lap seconds!)
    """
    ok = hours in xrange(0, 24)
    if ok:
        ok = minutes in xrange(0, 60)
    if ok:
        ok = seconds in xrange(0, 61)  # leap seconds!
        if seconds == 60:
            ok = minutes == 59
    if not ok and hours == 24 and minutes == 0 and seconds == 0:
        ok = True  # special iso8601 case for 24:00
    return ok


def iso8601_time_parser(input_string):
    """
    parse an ISO8601 time string

    :param input_string: ISO8601 time string
    :returns: dictionary with parsing results
    """
    work = input_string.replace(':', '')    # we always use the compact form
    work = work.replace(',', '.')   # dot or comma allowed, we use dot for parsing
    fraction = work.count('.')

    if fraction > 1:
        raise ValueError('ISO8601 only allows one fractional item for the time')
    elif fraction < 1:
        integer_part = work
        fraction_part = None
        fraction = None
    else:
        fraction = work.find('.')
        # iso 8601 allows only the least order part to have fraction
        # so at this point the input should be either
        # HH.nnnnnn
        # HHMM.nnnnnn
        # HHMMSS.nnnnnn
        if fraction not in [2, 4, 6] or input_string.rfind(':') > fraction:
            # we found a colon right of the decimal, not allowed in iso8601
            raise ValueError('invalid fractional part in time string')
        else:
            integer_part = work[:fraction]
            fraction_part = work[fraction + 1:]
            # keep where we have the fractional part for later
            if fraction == 2:
                fraction = 'hour'
            elif fraction == 4:
                fraction = 'minute'
            else:
                fraction = 'second'

    if not is_number(integer_part) or (fraction_part is not None and not is_number(fraction_part)):
        raise ValueError('ISO8601 time field contains non-numeric character')

    tlen = len(integer_part)
    if tlen not in [2, 4, 6]:
        raise ValueError('ISO8601 time field has invalid length')
    else:
        _hr = int(integer_part[0:2])
        _min = 0
        _sec = 0
        _format = 'hh'
        if tlen >= 4:
            _min = int(integer_part[2:4])
            _format = 'hh:mm'
        if tlen == 6:
            _sec = int(integer_part[4:6])
            _format = 'hh:mm:ss'

        if fraction is not None:
            _format += '.nn'

    if not is_valid_time(_hr, _min, _sec):
        raise ValueError('invalid time value (not in 00:00..24:00)')

    # now calculate microseconds since midnight
    micros = _hr * 3600000000
    micros += _min * 60000000
    micros += _sec * 1000000

    if fraction is not None:
        if fraction == 'hour':
            micros += long(_hr * 3600000000 * float('0.' + fraction_part))
        elif fraction == 'minute':
            micros += long(_min * 60000000 * float('0.' + fraction_part))
        elif fraction == 'second':
            micros += long(_sec * 1000000 * float('0.' + fraction_part))

        fraction_part = long(fraction_part)


    return {'hour': _hr, 'minute': _min, 'second': _sec, 'fraction_value': fraction_part,
            'iso_time': work, 'timeformat': _format, 'fraction': fraction, 'micros': micros}


def iso8601_timezone_parser(input_string):
    """
    parse ISO8601 time zone information

    time zone info is 'Z' or (+|-)hh[[:]mm]
    time zone is checked against a list of valid time zones (see definitions module)
    :param input_string: ISO8601 timezone string
    :returns: dictionary with parsing results
    """
    work = input_string.replace(':', '')
    tzlen = len(work)

    if input_string.upper() == 'Z':
        _h = 0
        _m = 0
        _off = '+'  # does not really matter :-)
    else:
        if tzlen not in [3, 5]:
            raise ValueError('time zone code has invalid length')
        else:
            _off = work[0]
            _h = int(work[1:3])
            if tzlen == 3:
                _m = '0'  # hours only means 0 minutes
            else:
                _m = int(work[3:5])

    # build a full tz string in canonical form and check if in list of valid timezones
    _tzstr = '{off}{hr:02d}:{mi:02d}'.format(off=_off, hr=_h, mi=_m)
    if _tzstr != '+00:00' and _tzstr not in definitions.VALID_TIMEZONES:
        raise ValueError('invalid timezone definition {tz}'.format(tz=_tzstr))

    _tzoffset = _h * 3600 + _m * 60
    if _off == '-':
        _tzoffset = _tzoffset * -1

    return {'tz_offset': _tzoffset, 'timezoneformat': '+TZ'}

    
def iso8601_date_string(year, month, day, isoformat='YYYY-MM-DD', separator='-'):
    """
    return a formatted string in ISO8601 syntax
    
    :return: ISO8601 long form (with separators) string according to the isoformat
    """
    if isoformat == 'YYYY':
        result = '{yr:04d}'.format(yr=year)
    elif isoformat == 'YYYY-MM':
        result = '{yr:04d}{sep}{mo:02d}'.format(yr=year, mo=month, sep=separator)
    elif isoformat == 'YYYY-MM-DD':
        result = '{yr:04d}{sep}{mo:02d}{sep}{dy:02d}'.format(yr=year, mo=month, dy=day, sep=separator)
    elif isoformat == 'YYYY-WWW':
        result = '{yr:04d}{sep}W{wk:02d}'.format(yr=year,
                                                 wk=week_of_year(year, month, day),
                                                 sep=separator)
    elif isoformat == 'YYYY-WWW-D':
        result = '{yr:04d}{sep}W{wk:02d}{sep}{wday:1d}'.format(yr=year,
                                                               wk=week_of_year(year, month, day),
                                                               wday=day_of_week(year, month, day, fmt='number'),
                                                               sep=separator)
    elif isoformat == 'YYYY-DDD':
        result = '{yr:04d}{sep}{doy:03d}'.format(yr=year,
                                                 doy=day_of_year(year, month, day),
                                                 sep=separator)
    else:
        raise ValueError('invalid iso format')
    return result
     
     
     
