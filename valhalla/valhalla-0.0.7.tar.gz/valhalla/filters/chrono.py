# -*- coding: utf-8 -*-

from datetime import datetime as m_datetime, date as m_date, time as m_time, timedelta as m_timedelta

from .. import ValidationError

_common_date_formats = {
	'american': '%m/%d/%Y',
	'american_expanded': '%d %b %Y',
	'american_scientific': '%Y-%m-%d',
	'europe': '%d/%m/%Y',
	'europe_expanded': '%d %b %Y'
}

_common_time_formats = {
	'civilian': '%I:%M:%S',
	'military': '%H:%M:%S'
}

_common_datetime_formats = {
	'unix_timestamp': '%Y-%m-%d %H:%M:%S'
}

def _ensure_datetime(chrono_obj):
	if isinstance(chrono_obj, m_date):
		chrono_obj = m_datetime.combine(chrono_obj, m_time.max)
	elif isinstance(chrono_obj, m_time):
		chrono_obj = m_datetime.combine(m_date.today(), chrono_obj)
	elif not isinstance(chrono_obj, m_datetime):
		raise ValidationError('This method requires a chronological object of some kind: [date, time, datetime]')

	return chrono_obj

# attempts to return a valid Date object
def date(format='%m/%d/%Y', _value=None, *args, **kwargs):
	try:
		format = _common_date_formats[format]
	except KeyError: pass

	try:
		dt = m_datetime.strptime(_value, format)
		return dt.date()
	except ValueError:
		raise ValidationError('There was a problem converting the value %s to a valid date.' % _value)


# attempts to return a valid Time object
def time(format='%I:%M:%S', _value=None, *args, **kwargs):
	try:
		format = _common_time_formats[format]
	except KeyError: pass

	try:
		dt = m_datetime.strptime(_value, format)
		return dt.time()
	except ValueError:
		raise ValidationError('There was a problem converting the value %s to a valid time.' % _value)

def datetime(format='%m/%d/%Y %I:%M:%S', _value=None, *args, **kwargs):
	try:
		format = _common_datetime_formats[format]
	except KeyError: pass

	try:
		dt = m_datetime.strptime(_value, format)
		return dt
	except ValueError:
		raise ValidationError('There was a problem converting the value %s to a valid date time.' % _value)

# validates that datetime is before specified datetime
def time_before(deadline, _value=None, *args, **kwargs):
	_value = _ensure_datetime(_value)
	deadline = _ensure_datetime(deadline)
	if _value > deadline:
		raise ValidationError('The date %s has exceeded the deadline of %s' % (_value, deadline))
	return _value

# validates that datetime is after specified datetime
def time_after(milestone, _value=None, *args, **kwargs):
	_value = _ensure_datetime(_value)
	milestone = _ensure_datetime(milestone)
	if _value < milestone:
		raise ValidationError('The date %s occurs before the specified milestone of %s' % (_value, milestone))
	return _value

# validates that datetime is between specified times
def time_between(milestone, deadline, _value=None, *args, **kwargs):
	_value = _ensure_datetime(_value)
	milestone = _ensure_datetime(milestone)
	deadline = _ensure_datetime(deadline)
	if _value < milestone or _value > deadline:
		raise ValidationError('The specified date/time does not fall within the required date range.')
	return _value