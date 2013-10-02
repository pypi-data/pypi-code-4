"""
PHP date() style date formatting
See http://www.php.net/date for format strings

Usage:
>>> import datetime
>>> d = datetime.datetime.now()
>>> df = DateFormat(d)
>>> print(df.format('jS F Y H:i'))
7th October 2003 11:39
>>>
"""
from __future__ import unicode_literals

import re
import time
import calendar

from tg.i18n import lazy_ugettext as _
from tg._compat import unicode_text

WEEKDAYS = {
    0:_('Monday'), 1:_('Tuesday'), 2:_('Wednesday'), 3:_('Thursday'), 4:_('Friday'),
    5:_('Saturday'), 6:_('Sunday')
}
WEEKDAYS_ABBR = {
    0:_('Mon'), 1:_('Tue'), 2:_('Wed'), 3:_('Thu'), 4:_('Fri'),
    5:_('Sat'), 6:_('Sun')
}
WEEKDAYS_REV = {
    'monday':0, 'tuesday':1, 'wednesday':2, 'thursday':3, 'friday':4,
    'saturday':5, 'sunday':6
}
MONTHS = {
    1:_('January'), 2:_('February'), 3:_('March'), 4:_('April'), 5:_('May'), 6:_('June'),
    7:_('July'), 8:_('August'), 9:_('September'), 10:_('October'), 11:_('November'),
    12:_('December')
}
MONTHS_3 = {
    1:_('jan'), 2:_('feb'), 3:_('mar'), 4:_('apr'), 5:_('may'), 6:_('jun'),
    7:_('jul'), 8:_('aug'), 9:_('sep'), 10:_('oct'), 11:_('nov'), 12:_('dec')
}
MONTHS_3_REV = {
    'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8,
    'sep':9, 'oct':10, 'nov':11, 'dec':12
}

re_formatchars = re.compile(r'(?<!\\)([aAbBcdDeEfFgGhHiIjlLmMnNoOPrsStTUuwWyYzZ])')
re_escaped = re.compile(r'\\(.)')


class Formatter(object):
    def format(self, formatstr):
        pieces = []
        for i, piece in enumerate(re_formatchars.split(unicode_text(formatstr))):
            if i % 2:
                pieces.append(unicode_text(getattr(self, piece)()))
            elif piece:
                pieces.append(re_escaped.sub(r'\1', piece))
        return ''.join(pieces)


class TimeFormat(Formatter):
    def __init__(self, t):
        self.data = t

    def a(self):
        "'a.m.' or 'p.m.'"
        if self.data.hour > 11:
            return _('p.m.')
        return _('a.m.')

    def A(self):
        "'AM' or 'PM'"
        if self.data.hour > 11:
            return _('PM')
        return _('AM')

    def B(self):
        "Swatch Internet time"
        raise NotImplementedError

    def f(self):
        """
        Time, in 12-hour hours and minutes, with minutes left off if they're
        zero.
        Examples: '1', '1:30', '2:05', '2'
        Proprietary extension.
        """
        if self.data.minute == 0:
            return self.g()
        return '%s:%s' % (self.g(), self.i())

    def g(self):
        "Hour, 12-hour format without leading zeros; i.e. '1' to '12'"
        if self.data.hour == 0:
            return 12
        if self.data.hour > 12:
            return self.data.hour - 12
        return self.data.hour

    def G(self):
        "Hour, 24-hour format without leading zeros; i.e. '0' to '23'"
        return self.data.hour

    def h(self):
        "Hour, 12-hour format; i.e. '01' to '12'"
        return '%02d' % self.g()

    def H(self):
        "Hour, 24-hour format; i.e. '00' to '23'"
        return '%02d' % self.G()

    def i(self):
        "Minutes; i.e. '00' to '59'"
        return '%02d' % self.data.minute

    def P(self):
        """
        Time, in 12-hour hours, minutes and 'a.m.'/'p.m.', with minutes left off
        if they're zero and the strings 'midnight' and 'noon' if appropriate.
        Examples: '1 a.m.', '1:30 p.m.', 'midnight', 'noon', '12:30 p.m.'
        Proprietary extension.
        """
        if self.data.minute == 0 and self.data.hour == 0:
            return _('midnight')
        if self.data.minute == 0 and self.data.hour == 12:
            return _('noon')
        return '%s %s' % (self.f(), self.a())

    def s(self):
        "Seconds; i.e. '00' to '59'"
        return '%02d' % self.data.second

    def u(self):
        "Microseconds; i.e. '000000' to '999999'"
        return '%06d' %self.data.microsecond


class DateFormat(TimeFormat):
    year_days = [None, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

    def __init__(self, dt):
        # Accepts either a datetime or date object.
        self.data = dt

    def b(self):
        "Month, textual, 3 letters, lowercase; e.g. 'jan'"
        return MONTHS_3[self.data.month]

    def B(self):
        "Month, textual, 3 letters, capitalized"
        return unicode_text(self.b()).capitalize()

    def c(self):
        """
        ISO 8601 Format
        Example : '2008-01-02T10:30:00.000123'
        """
        return self.data.isoformat()

    def d(self):
        "Day of the month, 2 digits with leading zeros; i.e. '01' to '31'"
        return '%02d' % self.data.day

    def D(self):
        "Day of the week, textual, 3 letters; e.g. 'Fri'"
        return WEEKDAYS_ABBR[self.data.weekday()]

    def e(self):
        "Timezone name if available"
        try:
            if hasattr(self.data, 'tzinfo') and self.data.tzinfo:
                # Have to use tzinfo.tzname and not datetime.tzname
                # because datatime.tzname does not expect Unicode
                return self.data.tzinfo.tzname(self.data) or ""
        except NotImplementedError:
            pass
        return ""

    def F(self):
        "Month, textual, long; e.g. 'January'"
        return MONTHS[self.data.month]

    def j(self):
        "Day of the month without leading zeros; i.e. '1' to '31'"
        return self.data.day

    def l(self):
        "Day of the week, textual, long; e.g. 'Friday'"
        return WEEKDAYS[self.data.weekday()]

    def L(self):
        "Boolean for whether it is a leap year; i.e. True or False"
        return calendar.isleap(self.data.year)

    def m(self):
        "Month; i.e. '01' to '12'"
        return '%02d' % self.data.month

    def M(self):
        "Month, textual, 3 letters; e.g. 'Jan'"
        return MONTHS_3[self.data.month].title()

    def n(self):
        "Month without leading zeros; i.e. '1' to '12'"
        return self.data.month

    def o(self):
        "ISO 8601 year number matching the ISO week number (W)"
        return self.data.isocalendar()[0]

    def O(self):
        "Difference to Greenwich time in hours; e.g. '+0200', '-0430'"
        seconds = self.Z()
        sign = '-' if seconds < 0 else '+'
        seconds = abs(seconds)
        return "%s%02d%02d" % (sign, seconds // 3600, (seconds // 60) % 60)

    def r(self):
        "RFC 2822 formatted date; e.g. 'Thu, 21 Dec 2000 16:01:07 +0200'"
        return self.format('D, j M Y H:i:s O')

    def S(self):
        "English ordinal suffix for the day of the month, 2 characters; i.e. 'st', 'nd', 'rd' or 'th'"
        if self.data.day in (11, 12, 13): # Special case
            return 'th'
        last = self.data.day % 10
        if last == 1:
            return 'st'
        if last == 2:
            return 'nd'
        if last == 3:
            return 'rd'
        return 'th'

    def t(self):
        "Number of days in the given month; i.e. '28' to '31'"
        return '%02d' % calendar.monthrange(self.data.year, self.data.month)[1]

    def U(self):
        "Seconds since the Unix epoch (January 1 1970 00:00:00 GMT)"
        return int(time.mktime(self.data.timetuple()))

    def w(self):
        "Day of the week, numeric, i.e. '0' (Sunday) to '6' (Saturday)"
        return (self.data.weekday() + 1) % 7

    def W(self):
        "ISO-8601 week number of year, weeks starting on Monday"
        # Algorithm from http://www.personal.ecu.edu/mccartyr/ISOwdALG.txt
        week_number = None
        jan1_weekday = self.data.replace(month=1, day=1).weekday() + 1
        weekday = self.data.weekday() + 1
        day_of_year = self.z()
        if day_of_year <= (8 - jan1_weekday) and jan1_weekday > 4:
            if jan1_weekday == 5 or (jan1_weekday == 6 and calendar.isleap(self.data.year-1)):
                week_number = 53
            else:
                week_number = 52
        else:
            if calendar.isleap(self.data.year):
                i = 366
            else:
                i = 365
            if (i - day_of_year) < (4 - weekday):
                week_number = 1
            else:
                j = day_of_year + (7 - weekday) + (jan1_weekday - 1)
                week_number = j // 7
                if jan1_weekday > 4:
                    week_number -= 1
        return week_number

    def y(self):
        "Year, 2 digits; e.g. '99'"
        return unicode_text(self.data.year)[2:]

    def Y(self):
        "Year, 4 digits; e.g. '1999'"
        return self.data.year

    def z(self):
        "Day of the year; i.e. '0' to '365'"
        doy = self.year_days[self.data.month] + self.data.day
        if self.L() and self.data.month > 2:
            doy += 1
        return doy

def format(value, format_string):
    "Convenience function"
    df = DateFormat(value)
    return df.format(format_string)

def time_format(value, format_string):
    "Convenience function"
    tf = TimeFormat(value)
    return tf.format(format_string)