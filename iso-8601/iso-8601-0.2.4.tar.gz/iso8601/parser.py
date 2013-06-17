import datetime
import re
import pytz

PARSED_CLASSES = (datetime.date,datetime.timedelta,)


try:
    import freezegun
except ImportError:
    pass
else:
    PARSED_CLASSES = PARSED_CLASSES + (freezegun.api.FakeDate,)

def parse(data):
    """
    Handle any of the valid ISO 8601 times, and convert to a python
    datetime object.
    
    >>> parse('2010-01-01')
    datetime.datetime(2010, 1, 1, 0, 0)
    >>> parse('2010-01-01T00:00:00')
    datetime.datetime(2010, 1, 1, 0, 0)
    >>> parse('2010-01-01 00:00:00')
    datetime.datetime(2010, 1, 1, 0, 0)
    >>> parse('2010-01-01 24:00:00')
    datetime.datetime(2010, 1, 2, 0, 0)
    >>> parse('2010-01-01 24:01:00')
    Traceback (most recent call last):
        ...
    ValueError: hour=24 is only permitted at midnight
    >>> parse('2010-01-01T24')
    datetime.datetime(2010, 1, 2, 0, 0)
    
    >>> parse('2010-01-01T01.5')
    datetime.datetime(2010, 1, 1, 1, 30)
    >>> parse('2010-01-01T01:01.5')
    datetime.datetime(2010, 1, 1, 1, 1, 30)
    >>> parse('2010-01-01T01:01:01.5')
    datetime.datetime(2010, 1, 1, 1, 1, 1, 500000)
    >>> parse('2010-01-01T24.5')
    Traceback (most recent call last):
        ...
    ValueError: hour=24 is only permitted at midnight
    >>> parse('2010-01-01T01.5:00')
    Traceback (most recent call last):
        ...
    ValueError: fractional time may only apply to last component
    >>> parse('2010-01-01T01.5:00.5')
    Traceback (most recent call last):
        ...
    ValueError: fractional time may only apply to last component
    
    >>> parse('P7D')
    datetime.timedelta(7)
    >>> parse('P14D')
    datetime.timedelta(14)
    >>> parse('P1DT')
    Traceback (most recent call last):
        ...
    ValueError: 'P1DT' does not match ISO8601 format
    >>> parse('P1D2H')
    Traceback (most recent call last):
        ...
    ValueError: 'P1D2H' does not match ISO8601 format
    >>> parse('P1DT2H')
    datetime.timedelta(1, 7200)
    >>> parse('P1Y')
    Traceback (most recent call last):
        ...
    ValueError: Year and month values are not supported in python timedelta
    
    >>> parse('2012-02-03T09:00:00Z')
    datetime.datetime(2012, 02, 03, 9, 0, tzinfo=<StaticTzInfo 'GMT'>)
    
    """
    
    if isinstance(data, PARSED_CLASSES):
        return data
    
    if 'P' in data:
        dt, duration = data.split('P')
        if dt:
            return parse(dt), parse_duration(duration)
        return parse_duration(duration)
        
    if 'T' not in data:
        data = data.replace(' ', 'T')
    
    if '-' not in data.split('T')[0]:
        basic = True
        DATE = "%Y%m%d"
    else:
        basic = False
        DATE = "%Y-%m-%d"
    
    if 'T' not in data:
        return datetime.datetime.strptime(data, DATE)
    
    if data[-1] == "Z":
        data = data.replace('Z', "+0000")
    
    if '+' in data:
        TIMEZONE = "%z"
        tzpart = data.split('+')[1]
        if len(tzpart) == 2:
            data += '00'
        if tzpart[2] and len(tzpart) == 5:
            data = data.replace(tzpart, tzpart.replace(':', ''))
    else:
        TIMEZONE = ""
    
    time = data.split('T')[1].replace(',', '.').split('+')[0]
    fraction = 0
    
    if time.count('.') > 1:
        raise ValueError('fractional time may only apply to last component')
    if time.count('.'):
        try:
            fraction = float("0.%s" %time.split('.')[1])
        except ValueError, arg:
            if arg.args[0].startswith('invalid literal for float():'):
                raise ValueError("fractional time may only apply to last component")
            raise
    
    time = time.split('.')[0]
    
    if basic:
        chars = len(time)
        if chars == 2:
            TIME = "%H"
        elif chars == 4:
            TIME = "%H%M"
        elif chars == 6:
            TIME = "%H%M%S"
    else:
        if time.count(':') == 0:
            TIME = "%H"
        elif time.count(':') == 1:
            TIME = "%H:%M"
        elif time.count(':') == 2:
            TIME = "%H:%M:%S"
    
    if "%S" in TIME:
        addition = datetime.timedelta(seconds=fraction)
    elif "%M" in TIME:
        addition = datetime.timedelta(minutes=fraction)
    elif "%H" in TIME:
        addition = datetime.timedelta(hours=fraction)
    
    if time.startswith('24'):
        no_hours = time[2:].replace(':','')
        if (no_hours != '' and int(no_hours) != 0) or addition:
            raise ValueError('hour=24 is only permitted at midnight')
        data = data.replace('T24', 'T00')
        add_day = True
    else:
        add_day = False
        
    date = datetime.datetime.strptime(data.split('+')[0].split('.')[0], DATE + 'T' + TIME)
    
    if add_day:
        date = date + datetime.timedelta(1)
    
    if TIMEZONE:
        if tzpart != '0000':
            raise ValueError("Unable to parse non-GMT values at this stage")
        date = date.replace(tzinfo=pytz.UTC)
    
    return date + addition

DATE_REGEX = r'(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)'

def parse_date(date):
    """
    >>> parse_date('2012-01-01')
    datetime.date(2012, 1, 1)
    >>> parse_date('2012-02-03T09:00:00')
    datetime.date(2012, 2, 3)
    """
    result = parse(date)
    if hasattr(result, 'date'):
        return result.date()
    return result

def parse_time(time):
    result = parse(date)
    if hasattr(result, 'time'):
        return result.time()
    return result


# TODO Allow least significant to be a float.
duration_regex = re.compile(
    r'^P?'
    r'((?P<years>\d+)Y)?'
    r'((?P<months>\d+)M)?'
    r'((?P<weeks>\d+)W)?'
    r'((?P<days>\d+)D)?'
    r'(T'
    r'((?P<hours>\d+)H)?'
    r'((?P<minutes>\d+)M)?'
    r'((?P<seconds>\d+)S)?'
    r')?$'
)

def duration_parts(duration):
    data = duration_regex.match(duration)
    if not data or duration[-1] == 'T':
        raise ValueError("'P%s' does not match ISO8601 format" % duration)
    return dict([(k,int(v)) for k,v in data.groupdict().items() if v and int(v)])

def parse_duration(duration):
    data = duration_parts(duration)
    if 'years' in data or 'months' in data:
        raise ValueError('Year and month values are not supported in python timedelta')
    return datetime.timedelta(**data)

def parse_interval(interval):
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()