# $Header: /vol/cscvs/python-Csys/Dates.py,v 1.6 2009/11/25 02:09:47 csoftmgr Exp $
# $Date: 2009/11/25 02:09:47 $
# @(#) $Id: Dates.py,v 1.6 2009/11/25 02:09:47 csoftmgr Exp $
#

import time, datetime
# import _getdate
import re
import Csys.DateTime as DateTime

# fix up patterns for Zope DateTime module
_tzPatterns = (
	# the ``-'' characters confuse the 2nd test
	(re.compile(r'^(\d{4})-(\d\d)-(\d\d)'), r'\1/\2/\3'),
	(re.compile(r'^(.*[-+]\d+)(.*)$'), r'\1'),
	(re.compile('AKDT'),	'US/Alaska'),
	(re.compile('AKST'),	'US/Alaska'),
	(re.compile('CST'),		'US/Central'),
	(re.compile('CDT'),		'US/Central'),
	(re.compile('EST'),		'US/Eastern'),
	(re.compile('EDT'),		'US/Eastern'),
	(re.compile('PST'),		'US/Pacific'),
	(re.compile('PDT'),		'US/Pacific'),
	# moves the time zone after the year in ``date'' output
	(re.compile(r'(.*)\s+([a-z/]+)\s+(\d{4})', re.IGNORECASE), r'\1 \3 \2'),
)
from types import StringTypes

_datetimeCache = {}


def date2datetime(s=None): #{
	'''Calculate and cache DateTime calculations'''
	if s: #{{
		rc = _datetimeCache.get(s)
		if rc is None: #{
			key = s
			if type(s) in StringTypes: #{
				for p, s1 in _tzPatterns: #{
					R = p.search(s)
					if R: #{
						s1 = p.sub(s1, s)
						s = s1
					#}
				#}
			#}
			rc = DateTime.DateTime(s)
			_datetimeCache[key] = rc
		#}
	#}
	else: #{
		rc = DateTime.DateTime()
	#}}
	return rc
#} date2datetime

def getdate(str): #{
	return long(date2datetime(str).timeTime())
#} getdate

__doc__ = '''Celestial Date Routines'''

minute			= 60
hour			= 60 * minute
day				= 24 * hour
week			= 7 * day
month			= 30 * day
year			= 365 * day

_str2secondTable = (
	# ('y',	year),
	('M',	month),
	('w',	week),
	('d',	day),
	('h',	hour),
	('m',	minute),
	('s',	1),
)
_str2secondsPattern = re.compile(r'[yMwdhm]')

def str2seconds(s): #{
	'''Convert [999y][999M][999w][999d][999h][999m][999] to seconds'''
	if _str2secondsPattern.search(s): #{{
		secs = 0
		for c, seconds in _str2secondTable: #{
			n = s.find(c)
			if n != -1: #{
				t, s = s[:n], s[n+1:]
				secs += int(t) * seconds
			#}
			if not s: break
		#}
		if s: secs += int(s)
	#}}
	else: #{
		secs = int(s)
	#}
	return secs
#} str2seconds

def seconds2str(seconds): #{
	'''Convert Seconds to string convertable by str2seconds'''
	s = ''
	for c, secs in _str2secondTable: #{
		i		= int(seconds/secs)
		if i > 0: s = s + '%d%s' % (i, c)
		seconds	= int(seconds % secs)
		if seconds <= 0: break
	#}
	return s;
#} seconds2str

# Date formats
DF_MM_DD_YY			= '%m/%d/%y'
DF_MM_DD_YYYY		= '%m/%d/%Y'
DF_SQLDATE			= '%Y-%m-%d'
DF_SQLDATETIME		= '%Y-%m-%d %H:%M:%S'
DF_UDATE			= None
DF_YYYY				= '%Y'
DF_YYYYMM			= '%Y%m'
DF_YYYYMMDD			= '%Y%m%d'
DF_YYYYMMDDHH		= '%Y%m%d%H'
DF_YYYYMMDDHHMM		= '%Y%m%d%H%M'
DF_YYYYMMDDHHMMSS	= '%Y%m%d%H%M%S'
DF_YYYY_MM_DD 		= '%Y/%m/%d'
# These will be used for archiving Maildir folders
DF_YYYYdMMdDD 		= '%Y.%m.%d'
DF_YYYYdMM 			= '%Y.%m'
DF_MAIL				= '%a,  %d  %b %Y %H:%M:%S %z'

defaultFlag			= DF_SQLDATE

def setDefaultFlag(flag): #{
	'''Set default Conversion format'''
	global defaultFlag
	defaultFlag = flag
#} setDefaultFlag

def _fmt(mytime=None, flag=defaultFlag): #{
	'''internal format routine'''
	if not mytime: mytime = time.time()
	if not flag: return mytime
	if flag != DF_MAIL: tm = time.localtime(mytime)
	else: tm = time.gmtime(mytime)
	return(time.strftime(flag, tm))
#} _fmt

mailFmt = '%a, %d %b %Y %H:%M:%S '

def rfcDate(mytime=None): #{
	'''
	Return RFC822-conformant date string based on the
	displacement of the local time zone from UTC.
	'''
	if mytime is None: mytime = time.time()
	loctime = time.localtime(mytime)
	utctime = time.gmtime(mytime)
	return (
		time.strftime(mailFmt, loctime) +
		'%05d' % ((time.mktime(loctime) - time.mktime(utctime))/36)
	)
#} rfcDate

def today(mytime=None, flag=defaultFlag): #{
	'''Today's date'''
	if not mytime: mytime = time.time()
	return _fmt(mytime, flag)
#} today

def yesterday(mytime=None, flag=defaultFlag): #{
	'''Yesterday's time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - day, flag))
#} yesterday

def tomorrow(mytime=None, flag=defaultFlag): #{
	'''Tomorrow'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + day, flag))
#} tomorrow

def lastweek(mytime=None, flag=defaultFlag): #{
	'''One week before time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - week, flag))
#} lastweek

def nextweek(mytime=None, flag=defaultFlag): #{
	'''One week after time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + week, flag))
#} nextweek

def lastmonth(mytime=None, flag=defaultFlag): #{
	'''One month before time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - month, flag))
#} lastmonth

def nextmonth(mytime=None, flag=defaultFlag): #{
	'''One month after time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + month, flag))
#} nextmonth

def lastyear(mytime=None, flag=defaultFlag): #{
	'''One year before time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - year, flag))
#} lastyear

def nextyear(mytime=None, flag=defaultFlag): #{
	'''One year after time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + year, flag))
#} nextyear

# relative dates
def dayfrom(mytime=None, flag=defaultFlag, days=1): #{
	'''Day From'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + days * day, flag))
#} dayfrom

def daybefore(mytime=None, flag=defaultFlag): #{
	'''Yesterday's time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - day, flag))
#} daybefore

def dayafter(mytime=None, flag=defaultFlag): #{
	'''Tomorrow'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + day, flag))
#} dayafter

def weekbefore(mytime=None, flag=defaultFlag): #{
	'''One week before time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - week, flag))
#} weekbefore

def weekafter(mytime=None, flag=defaultFlag): #{
	'''One week after time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + week, flag))
#} weekafter

def monthbefore(mytime=None, flag=defaultFlag): #{
	'''One month before time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - month, flag))
#} monthbefore

def monthafter(mytime=None, flag=defaultFlag): #{
	'''One month after time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + month, flag))
#} monthafter

def yearbefore(mytime=None, flag=defaultFlag): #{
	'''One year before time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime - year, flag))
#} yearbefore

def yearafter(mytime=None, flag=defaultFlag): #{
	'''One year after time'''
	if not mytime: mytime = time.time()
	return(_fmt(mytime + year, flag))
#} yearafter

# from datestr.c file
# YYYY-MM-DD

_yyyy_mm_dd_re	= re.compile(r'^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})$')
# MM/YY/YY(YY)
_mm_dd_year_re	= re.compile(r'^([0-9]{1,2})/([0-9]{1,2})/([0-9]{2,4})$')
# (M)MDDYYYY
_mmddyear_re	= re.compile(r'^([0-9]{1,2})([0-9]{2})([0-9]{4})$')
# increment for today's date
_9999_re		= re.compile(r'^(-{0,1}[0-9]{1,4})$')

def strdate(date_in, fmt=DF_SQLDATE): #{
	'''Convert date to proper date field

	This routine expects dats in the format mm/dd/yyyy, mm.dd.yyyy, or an
	integer which can be converted to a data by adding/subtracting that
	integer from the current date.
	'''
	if _str2secondsPattern.search(date_in): #{
		date_in = str(str2seconds(date_in)/day)
	#}
	while True: #{ # allow break to minimize code
		r = _yyyy_mm_dd_re.search(date_in)
		if r: break # this is what we want at the end
		date_in = date_in.replace('.', '/').strip()
		if not date_in or date_in == '**/**/**' or date_in == '0000-00-00': return(None)
		r = _mm_dd_year_re.search(date_in)
		if not r: r = _mmddyear_re.search(date_in)
		if r: #{
			_month, _day, _year = (
				int(r.group(1)), int(r.group(2)), int(r.group(3)))
			if _year < 70: _year += 2000
			elif _year < 100: _year += 1900
			if _year < 1980: _year += 100
			date_in = '%02d-%02d-%04d' % (_month, _day, _year)
			# print 'date_in: ', date_in
			date_in = today(getdate(date_in), fmt)
			break
		#}
		r = _9999_re.search(date_in)
		if r: #{
			date_in = today(time.time() + int(r.group(1)) * day, fmt)
			break
		#}
		date_in = today(getdate(date_in), fmt)
		break
	#}
	else: #{
		unerrs('strdate: invalid date %s' % date_in)
		return(None)
	#}
	return(date_in)
#} strdate

def datecnv(date_in): return(strdate(date_in))

def datestr(date_in): return(strdate(date_in))

def curdate(fmt=DF_SQLDATE): #{
	'''Current Date'''
	return today(flag=fmt)
#} curdate

Curdate = curldate = curdate

def strtime(hr_min): #{
	'''Convert and valid HH:MM'''
	hour, minutes = [ int(x) for x in hr_min.split(':') ]
	if not 0 <= hour <= 24: #{
		unerrs('strtime: hours %d < 0 or > 24' % hour)
		raise ValueError
	#}
	if not 0 < minutes < 59: #{
		unerrs('strtime: minutes %d < 0 or > 59' % minutes)
		raise ValueError
	#}
	return ('%02d:%02d' % (hour, minutes))
#} strtime

def curtime(): #{
	'''Return current time as HH:MM'''
	return time.strftime('%H:%M', time.localtime())
#} curtime

def utime2datetime(utime): #{
	'''Convert Unix time to datetime accurate to seconds'''
	t = time.localtime(utime)[:6]
	return datetime.datetime(*t)
#} utime2datetime

def str2datetime(s): #{
	'''Convert time string to datetime accurate to seconds'''
	return utime2datetime(getdate(s))
#} str2datetime

def utime2date(utime): #{
	'''Convert Unix time to date accurate to seconds'''
	t = time.localtime(utime)[:3]
	return datetime.date(*t)
#} utime2date

def str2date(s): #{
	'''Convert time string to dateaccurate to seconds'''
	date_in = strdate(s)
	if date_in is None: return None
	return utime2date(getdate(date_in))
#} str2datetime

if __name__ == '__main__': #{
	import sys
	print 'OK'
	print rfcDate()
	print curdate(DF_SQLDATETIME)
	# time.sleep(10)
	print strdate('01/31/2004')
	print today(getdate('01/31/2004'))
	print today(getdate('2004-01-31'))
	print today(getdate('1/1/00'))
	print curdate(DF_SQLDATETIME)
	sys.exit(0)
	print 'strtime: %s' % strtime('3:15')
	secs = str2seconds('1d23h37m15s')
	print secs
	print seconds2str(171481)
	print str2date('1.1.2006')
	print str2date('02012008')
	print str2date('-1')
	print str2date('**/**/**')
	print str2date('1w3d')
	print getdate('Sat, 29 Mar 2008 22:45:45 +0100 (CET)')
	print time.time()
	print getdate(long(time.time()))
	print _datetimeCache
	sys.exit(0)
	flag = DF_SQLDATE
	flag = DF_YYYYMMDDHHMMSS
	flag = DF_MAIL
	print flag
	print 'today\t\t' + today(flag=flag)
	print 'yesterday\t' + yesterday(flag=flag)
	print 'tomorrow\t' + tomorrow(flag=flag)
	print 'last week\t' + lastweek(flag=flag)
	print 'nextweek\t' + nextweek(flag=flag)
	print 'lastmonth\t' + lastmonth(flag=flag)
	print 'nextmonth\t' + nextmonth(flag=flag)
	print 'lastyear\t' + lastyear(flag=flag)
	print 'nextyear\t' + nextyear(flag=flag)
	print 'dayfrom\t\t' + dayfrom(flag=flag)
	print 'daybefore\t' + daybefore(flag=flag)
	print 'dayafter\t' + dayafter(flag=flag)
	print 'weekbefore\t' + weekbefore(flag=flag)
	print 'weekafter\t' + weekafter(flag=flag)
	print 'monthbefore\t' + monthbefore(flag=flag)
	print 'monthafter\t' + monthafter(flag=flag)
	print 'yearbefore\t' + yearbefore(flag=flag)
	print 'yearafter\t' + yearafter(flag=flag)
#}
