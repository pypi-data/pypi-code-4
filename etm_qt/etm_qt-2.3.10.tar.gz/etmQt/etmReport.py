# coding=UTF-8
from __future__ import print_function #, unicode_literals

from optparse import OptionParser, OptParseError, OptionError, OptionConflictError, BadOptionError, OptionValueError
import re
from dateutil.parser import parse

from etmData import get_options
from etmData import comma_regex, parse_datetime, sortdatefmt


wrap = 15
minimum = 30
opening = "8:00am"
closing = "5:00pm"
include = "Bfc"

parser_msg = []
attrs = {}
all_off = ''

arg_regex = re.compile(r'\s+-')

user_settings, settings = get_options()

def make_csv(fname, tuples, options):
    if options:
        items, options = opts2Tuples(tuples, options)
    else:
        items = tuples
    include = re.split('\s*,\s*', options['values'])
    keys = [19, 3, 17] + [int(fieldNum[x]) for x in include]
    lines = []
    hdrlst = ['"%s"' % tupleKeys[x] for x in keys]
    lines.append(",".join(hdrlst))
    for item in items:
        line = []
        for key in keys:
            line.append('"%s"' % item[key])
        lines.append(",".join(line))
    out = "\n".join(lines)
    if fname:
        (name, ext) = os.path.splitext(fname)
        pname = os.path.join(export, "%s.csv" % name)
        fo = codecs.open(pname, 'wb', file_encoding)
        fo.write(out)
        fo.close()
        return('exported to %s' % fname)
    else:
        return(out)

def make_ical():
    cal = vobject.iCalendar()
    cal.add('prodid').value = '-//etm %s//dgraham.us//' % version
    cal.add('version').value = '2.0'
    for id, hsh in id2hash.items():
        now = datetime.datetime.now()
        now = now.replace(tzinfo=tzlocal()).astimezone(tzutc())
        if '_z' in hsh:
            timezone = hsh['_z']
        else:
            timezone = None

        itemType = hsh[u'leader'][0]
        if itemType in ['*']:
            element = cal.add('vevent')
        elif itemType in ['-', '+', '~', '%']:
            # since actions do not have a starting time, we treat them as todos
            element = cal.add('vtodo')
        elif itemType in ['!']:
            element = cal.add('vjournal')
        element.add('uid').value = uuid4().hex
        element.add('dtstamp').value = now
        element.add('last_modified').value = now
        element.add('summary').value = hsh['_summary']
        if 'l' in hsh:
            element.add('location').value = hsh['l']
        if 'd' in hsh:
            element.add('description').value = hsh['n']
        if 'p' in hsh:
            try:
                p = int(hsh['p'])
                assert(p >= 1 and p <= 9)
                element.add('priority').value = p
            except:
                pass
        if 't' in hsh:
            element.add('categories').value = hsh['t']


# this seems to be the one used in etmWX
def make_vcal(fname, tuples, options):
    """
        Only filter tuples if options is non-null. Return calendar as string
        if fname is ''.
    """
    if not has_vobject:
        return('')
    ret_val = False
    if options:
        items, options = opts2Tuples(tuples, options)
    else:
        items = tuples
    cal = vobject.iCalendar()
    cal.add('prodid').value = '-//etm %s//dgraham.us//' % version
    cal.add('version').value = '2.0'
    for item in items:
        item = list(item)
        tmp = []
        for i in range(len(item)):
            if type(item[i]) == str:
                try:
                    tmp.append(unicode(item[i]))
                except:
                    print("except", item[i], type(item[i]), sys.exc_info())
        if item[3] == sortOrder['begin']:
            continue
        if item[0]:
            dtl = datetime.datetime(item[0],item[1],item[2], 0, 0,
                    tzinfo=tzlocal())
            dtu = dtl.astimezone(tzutc())
            dd = dtu.date()
        else:
            dtl = dtu = dd = ''
        if item[3] in [sortOrder['allday'],
                sortOrder['event'],
                sortOrder['reminder']]:
            dt = dtl
            element = cal.add('vevent')
        elif item[3] in [sortOrder['pastdue'],
                sortOrder['waiting'],
                sortOrder['waiting'],
                sortOrder['task'],
                sortOrder['undated'],
                sortOrder['finished']]:
            dt = dd
            element = cal.add('vtodo')
        elif item[3] in [sortOrder['action'], sortOrder['note']]:
            dt = dtu
            element = cal.add('vjournal')
        element.add('uid').value = uuid4().hex
        if item[6] and not no_regex.match(item[6]):
            element.add('priority').value = item[6][-1]
        if item[17]:
            element.add('summary').value = item[17]
        if item[13] and not no_regex.match(item[13]):
            element.add('location').value = item[13]
        if item[23] and not no_regex.match(item[23]):
            element.add('categories').value = item[23]
        if item[24]:
            #  element.add('description;CHARSET=UTF-8', item[24])
            element.add('description').value = item[24]
        if dt:
            #  if item[3] in [4,5,6,8,10]: # dated task or note
            if item[3] in [sortOrder['pastdue'],
                    sortOrder['task'],
                    sortOrder['waiting'],
                    sortOrder['begin'],
                    ]: # dated task
                element.add('due').value = dd
                allday =False
            elif item[3] in [sortOrder['finished']]: # completed task
                element.add('completed').value = dtu
                allday =False
            if item[3] in [sortOrder['undated']]: # undated task
                allday =False
            elif item[3] in [sortOrder['note']]: # note
                element.add('dtstart').value = dtu
            elif item[3] in [sortOrder['allday']]: # allday
                allday = True
                element.add('dtstart').value = dd
            elif item[3] in [sortOrder['action']]: # action
                element.add('comment').value = "%s minutes" % item[5]
                allday =False
            elif item[3] in [sortOrder['event'], sortOrder['reminder']]:
                allday = False
                minute = int(item[4])
                h = min(23, minute//60)
                m = minute%60
                try:
                    dtl = dt.replace(hour=h, minute=m, second=0)
                    dtu = dtl.astimezone(tzutc())
                except:
                    print("Exception", minute, h, m, item)
                element.add('dtstart').value = dtu
                if item[5] and item[5] > 0:
                    p_min = int(item[5])
                    minute += p_min
                    h = min(23, minute//60)
                    m = minute%60
                    s = 0
                    if h >= 24:
                        h = 23
                        m = 59
                        s = 59

                    dtl = dt.replace(hour=h, minute=m, second=s)
                    dtu = dtl.astimezone(tzutc())
                    element.add('dtend').value = dtu
        ret_val = True
    if fname:
        (name, ext) = os.path.splitext(fname)
        pname = os.path.join(export, "%s.ics" % name)
        try:
            cal_str = cal.serialize()
        except:
            cal.prettyPrint()
            print(sys.exc_info())
            sys.exit()
        fo = open(pname, 'wb')
        try:
            fo.write(cal_str)
        except:
            print("EXCEPTION", sys.exc_info())
        fo.close()
        return(ret_val, 'exported as vCal to %s' % fname)
    else:
        return(ret_val, cal.serialize())

def busytimesReport(busytimes, options):
    """
    busytimes = {}
    date -> [(isocal-datekey, start_minutes, end_minutes, uuid,  total_minutes, f)]

    Input a hash of lists (datetime -> list of busy intervals) and return busy
    bars and free lists, the latter reflecting the values of earliest (time),
    latest (time) and minimum (minutes).
    form a list using bisect
    starting key = YR|MN|DY|WN
       YR | WN | "busy|free|confict" | MN | DY | "bar|times"
    """
    start = parse("%s-%s-%s" % options['begin_date'])
    end = parse("%s-%s-%s" % options['end_date'])
    earliest = parse(options['opening'])
    earliest_minute = earliest.hour * 60 + earliest.minute
    latest = parse(options['closing'])
    latest_minute = latest.hour * 60 + latest.minute
    starthour = earliest.hour
    endhour = latest.hour
    if latest.minute > 0:
        endhour += 1
    if 'wrap' in options:
        wrap = int(options['wrap'])
    if 'minimum' in options:
        minimum = int(options['minimum'])
    cols = (endhour - starthour)*(60/slotsize) + 15
    busyTuples = []
    tmpList = []
    twdth = cols - 15
    date = start
    keys = busy.keys()
    while date < end:
        busy_times = []
        free_times = []
        conflict_times = []
        busy_bars = []
        free_bars = []
        begW = (date - (date.weekday()) * oneday).strftime(date_fmt)
        endW = (date + (6-date.weekday()) * oneday).strftime(end_date_fmt)
        yr, mn, dy, h, m, wn, wa, ma  = date.strftime(
                    "%Y,%m,%d,%H,%M,%W,%a,%b").split(',')
        # iso week number correction
        wn = (date - (date.weekday()) * oneday).isocalendar()[1]
        print("week number", wn)
        ws = "week %2s: %s - %s" % (wn, begW, endW)
        ds = "%s %s %s" % (wa, ma, dy)
        date = date + oneday

        #  busy keys have the form (y,m,d)
        d = tuple(map(int, (yr,mn,dy)))
        if d in busy:
            b = busy[d]
        else:
            b = []
        if len(b) > 0:
            try:
                b_times, f_times, c_times = processBusy(
                        earliest_minute, latest_minute, minimum, wrap, b)
                bbar_str = "".join(MarkList(b_times, earliest_minute,
                    latest_minute, busychar, slotsize, c_times))
                s = l2s(b_times).strip()
                if s:
                    btime_lines = text_wrap("%s" % s, width = twdth)
                else:
                    btime_lines = ['']
                fbar_str = "".join(MarkList(f_times, earliest_minute,
                    latest_minute, freechar, slotsize))
                s = l2s(f_times).strip()
                if s:
                    ftime_lines = text_wrap("%s" % s, width = twdth)
                else:
                    ftime_lines = ['']
                s = l2s(c_times).strip()
                if s:
                    ctime_lines = text_wrap("%s" % s, width = twdth)
                else:
                    ctime_lines = []
                busy_bars = bbar_str
                if btime_lines:
                    lines = []
                    lines.append("%s" % (btime_lines.pop(0).strip()))
                    for line in btime_lines:
                        lines.append("%s%s" % (" "*14,
                            line.strip()))
                    busy_times = "\n".join(lines)
                free_bars = fbar_str
                if ftime_lines:
                    lines = []
                    lines.append("%s" % (ftime_lines.pop(0).strip()))
                    for line in ftime_lines:
                        lines.append("%s%s" % (" "*14,
                            line.strip()))
                    free_times = "\n".join(lines)
                if ctime_lines:
                    lines = []
                    lines.append(ctime_lines.pop(0).strip())
                    for line in ctime_lines:
                        lines.append("%s%s" % (" "*14,
                            line.strip()))
                    conflict_times = "\n".join(lines)
            except:
                print("except:", d, earliest, latest, minimum, b)
                print(sys.exc_info())
        else:
            busy_times = ""
            busy_bars = "".join(SlotList(starthour, endhour, slotsize))
            free_times = l2s([[earliest_minute, latest_minute]])
            free_bars = "".join(MarkList([[earliest_minute, latest_minute]],
                earliest_minute, latest_minute, freechar, slotsize))
        bisect.insort(tmpList, tuple((yr,ws,'bb',mn,dy,ds,busy_bars)))
        bisect.insort(tmpList, tuple((yr,ws,'bt',mn,dy,ds,busy_times)))
        bisect.insort(tmpList, tuple((yr,ws,'fb',mn,dy,ds,free_bars)))
        bisect.insort(tmpList, tuple((yr,ws,'ft',mn,dy,ds,free_times)))
        if conflict_times:
            bisect.insort(tmpList, tuple((yr,ws,'c',mn,dy,ds, conflict_times)))

    dt = []
    for k, g in group_sort(tmpList, (0,1)):
        dt.append((k[1], '', 'blue'))
        for l, h in group_sort(g, 2):
            if l == 'bb' and 'B' in options['include']:
                dt.append(('  Busy', 'em', 'green'))
                dt.append(("    %s" % HourBar(starthour, endhour, slotsize),))
                for i in h:
                    dt.append(("    %s: %s" % (i[5], i[6]),))
                dt.append(("",))
            elif l == 'bt' and 'b' in options['include']:
                dt.append(('  Busy Times', 'em', 'green'))
                for i in h:
                    dt.append(("    %s: %s" % (i[5], i[6]),))
                dt.append(("",))
            elif l == 'fb' and 'F' in options['include']:
                dt.append(('  Free', 'em', 'green'))
                dt.append(("    %s" % HourBar(starthour, endhour, slotsize),))
                for i in h:
                    dt.append(("    %s: %s" % (i[5], i[6]),))
                dt.append(("",))
            elif l == 'ft' and 'f' in options['include']:
                dt.append(('  Free Times', 'em', 'green'))
                for i in h:
                    dt.append(("    %s: %s" % (i[5], i[6]),))
                dt.append(("",))
            elif l == 'c' and 'c' in options['include']:
                dt.append(( '  Conflicts', 'em', 'red' ))
                for i in h:
                    dt.append(("    %s: %s" % (i[5], i[6]),))
                dt.append(("",))
    while dt and not dt[-1]:
        dt.pop(-1)
    return(dt)

### Parsers ###
class ETMOptParser(OptionParser):
    def error(self, m):
        global parser_msg
        print(m)
        parser_msg.append(m)

optionParms = {}

optionParms['begin_date'] = ("-b", "store", "begin_date", None,
"""Fuzzy parsed date. Limit the display of dated items to those whose dates fall ON OR AFTER this date. Relative day and month expressions can also be used so that, for example, '-b -14' would begin 14 days before the current date and '-b -1/1' would begin on the first day of the previous month. Default: None.""")

optionParms['end_date'] = ("-e", "store", "end_date", None, # soon_tup,
"""Fuzzy parsed date. Limit the display of dated items to those whose dates fall BEFORE this date (fuzzy parsed). As with 'begin_date' relative month expressions can be used so that, for example, '-b -1/1  -e +1/1' would include all items from the last and current months. Default: None. """)

optionParms['path'] = ("-p", "store", 'path', None,
"""Regular expression. Limit the display of items to those from files whose paths match PATH (ignoring case). Prepend an exclamation mark, i.e., use !PATH rather than PATH, to limit the display of items to those from files whose paths do NOT match PATH.""")

optionParms['context'] =("-c", "store", 'context', None,
"""Regular expression. Limit the display to items with contexts matching CONTEXT (ignoring case). Prepend an exclamation mark, i.e., use !CONTEXT rather than CONTEXT, to limit the display to items which do NOT have contexts matching CONTEXT.""")

optionParms['tag'] =("-t", "append", 'tag', None,
"""Regular expression. Limit the display to items with tags matching TAG (ignoring case) . Prepend an exclamation mark, i.e., use !TAG rather than TAG, to limit the display to items with tags that do NOT match TAG. This switch can be used more than once, e.g., use '-t tag 1 -t tag 2' to match items with tags that match 'tag 1' and 'tag 2'.""")

optionParms['keyword'] = ("-k", "store", 'keyword', None,
"""Regular expression. Limit the display to items with keywords matching KEYWORD (ignoring case). Prepend an exclamation mark, i.e., use !KEYWORD rather than KEYWORD, to limit the display to items with keywords that do NOT match KEYWORD.""")

optionParms['location'] = ("-l", "store", 'location', None,
"""Regular expression. Limit the display to items with location matching LOCATION (ignoring case). Prepend an exclamation mark, i.e., use !LOCATION rather than LOCATION, to limit the display to items with locations that do NOT match LOCATION.""")

optionParms['user'] = ("-u", "store", 'user', None,
"""Regular expression. Limit the display to items with user matching USER (ignoring case). Prepend an exclamation mark, i.e., use !USER rather than USER, to limit the display to items with users that do NOT match USER.""")

optionParms['search'] = ("-s", "store", 'search', None,
"""Regular expression. Limit the display to items containing SEARCH (ignoring case) in either the summary or in the description. Prepend an exclamation mark, i.e., use !SEARCH rather than SEARCH, to limit the display to items which do NOT contain SEARCH in either the summary or the description.""")

optionParms['omit'] = ("-o", "store", 'omit', None,
"""String. Show/hide a)ctions, all d)ay events, scheduled  e)vents, f)inished tasks, n)otes, r)eminders, all t)asks, u)ndated tasks and/or w)aiting tasks depending upon whether omit contains 'a', 'd', 'e', 'f', 'n', 'r', 't', 'u' and/or 'w' and begins with '!' (show) or does not being with '!' (hide). Default: %default.""")

optionParms['groupby'] = ("-g", "store", 'cols', '((y, m, d),)',
"""A tuple of elements from y (year), m (month), d (day), w (week number in year), q (quarter number), c (context), k (keyword), l (location), f (file path) and u (user). For example, the default, -g ((y, m, d),), sorts by year, month and day together to give output such as                                                                       \n
|   Fri Apr 1 2011                                                           \n
|       items for April 1                                                    \n
|   Sat Apr 2 2011                                                           \n
|       items for April 2                                                    \n
|   ...                                                                      \n
As another example, -g ((y, q), m, d), would sort by year and quarter, then month and finally day to give output such
as
                                                                             \n
|   2011 2nd quarter                                                         \n
|       Apr                                                                  \n
|           Fri 1                                                            \n
|               items for April 1                                            \n
|           Sat 2                                                            \n
|               items for April 2                                            \n
|   ...                                                                      \n
""")

optionParms['details'] = ("-d", "store", 'details', 1,
"""String. Controls the display of item details. With '-d 0', item details would
not be displayed. With '-d 1' (the default), the prefix and summary would be
displayed. With '-d led', for example, a second details line would be appended
displaying the item l)ocation, e)xtent and d)escription entries.""")

optionParms['wrap'] = ("-w",  "store", 'wrap', wrap,
"""Positive integer. Provide a buffer of WRAP minutes before and after busy
periods when computing free periods. Default: %default.""")

optionParms['minimum'] = ("-m", "store", 'minimum', minimum,
 """Positive integer. The minimum length in minutes for an unscheduled period
 to be displayed. Default: %default.""")

optionParms['opening'] = ("-O", "store", 'opening', opening,
 """Time. The opening or earliest time (fuzzy parsed) to be considered when
 displaying unscheduled periods. Default: %default.""")

optionParms['closing'] = ("-C", "store", 'closing', closing,
 """Time. The closing or latest time (fuzzy parsed) to be considered when
 displaying unscheduled periods. Default: %default.""")

optionParms['include'] = ("-i", "store", 'include', include,
"""String containing one or more characters from B (busy time bars), b (busy times), F (free time bars), f (free times), and c (conflict times). Default: %default""")

#### end of parms ####

parserOpts = {}


parserOpts['outline'] = [
    'begin_date', 'end_date', 'path', 'context', 'keyword', 'tag',
    'user', 'location', 'search', 'omit', 'groupby', 'details'
    ]

parserOpts['busy'] = [
    'begin_date', 'end_date', 'path', 'include', 'context', 'keyword',
    'tag', 'user', 'search', 'opening', 'closing', 'minimum', 'wrap'
    ]

parserOpts['day'] = [
    'begin_date', 'end_date', 'path', 'context', 'keyword', 'tag',
    'user', 'location', 'search', 'omit'
    ]

parserOpts['next'] = [
    'path', 'context', 'keyword', 'tag', 'user', 'location',
    'search', 'omit'
    ]

parserOpts['pastdue'] = [
    'path', 'context', 'keyword', 'tag', 'user', 'location',
    'search', 'omit'
    ]

parserOpts['folder'] = [
    'begin_date', 'end_date', 'path', 'context', 'keyword', 'tag',
    'user', 'location', 'search', 'omit'
    ]

parserOpts['keyword'] = [
    'begin_date', 'end_date', 'path', 'context', 'keyword', 'tag',
    'user', 'location', 'search', 'omit'
    ]

parserOpts['tag'] = [
    'begin_date', 'end_date', 'path', 'context', 'keyword', 'tag',
    'user', 'location', 'search', 'omit'
    ]


def getOpts(repType, l=[]):
    parser = ETMOptParser(usage = '')
    for opt in parserOpts[repType]:
        # print("checking opt", opt)
        s, a, dst, dflt, hlp = optionParms[opt]
        if dflt:
            parser.add_option(s, action = a, dest = dst, default = dflt,
                    help = hlp)
        else:
            parser.add_option(s, action = a, dest = dst,  help = hlp)
    if l:
        (opts, args) = parser.parse_args(l)
    else:
        (opts, args) = parser.parse_args()
    opts.__dict__['args'] = args
    if 'begin_date' in opts.__dict__:
        opts.__dict__['begin_date'] = parse(parse_datetime(
                    # opts.__dict__['begin_date'])).replace(tzinfo=None)
                    opts.__dict__['begin_date'])).date()
    if 'end_date' in opts.__dict__:
        opts.__dict__['end_date'] = parse(parse_datetime(
                    # opts.__dict__['end_date'])).replace(tzinfo=None)
                    opts.__dict__['end_date'])).date()
    return(opts.__dict__)

def getOptsFromString(s):
    print("str:", s)
    # l = s.split('-')
    l = arg_regex.split(s)
    p_type = l.pop(0).strip()
    args = []
    for x in l:
        if not len(x) > 1: continue
        args.extend(["-%s" % x[0], "%s" % x[1:].strip()])
    return(p_type, getOpts(nameHash[p_type], args))


def parse_opts(options):
    # FIXME: all this is from the old etmParsers.py
    beg_dt, today, soondate = getToday()
    if 'begin_date' in options and options['begin_date']:
        if type(options['begin_date']) == tuple:
            beg_dt = parse("%s-%s-%s" % options['begin_date'])
        else:
            m = rel_monthdate_regex.match(options['begin_date'])
            if m:
                beg_dt = rel_monthday2date(*m.groups())
            else:
                m = rel_date_regex.match(options['begin_date'])
                if m:
                    # we have a relative date in the form '+|- integer'.
                    if m.group(1) == '+':
                        beg_dt = datetime.datetime.today() + int(m.group(2)) * oneday
                    elif m.group(1) == '-':
                        beg_dt = datetime.datetime.today() - int(m.group(2)) * oneday
                else:
                    try:
                        beg_dt = parse(options['begin_date'])
                    except:
                        print("could not parse date '%s'" % options['begin_date'])
                        beg_dt = datetime.date.today()
            options['begin_date'] = tuple(map(int,
                beg_dt.strftime("%Y,%m,%d").split(',')))
    else:
        beg_dt = datetime.date.today()
        options['begin_date'] = tuple(map(int,
                beg_dt.strftime("%Y,%m,%d").split(',')))
    if 'end_date' in options and options['end_date']:
        if type(options['end_date']) != tuple:
            m = rel_monthdate_regex.match(options['end_date'])
            if m:
                end_dt = rel_monthday2date(*m.groups())
            else:
                m = rel_date_regex.match(options['end_date'])
                if m and m.group(1) == '+':
                    # we have a relative date in the form '+|- integer'.
                    beg_dt = parse("%d-%02d-%02d" % options['begin_date'])
                    end_dt = beg_dt + int(m.group(2)) * oneday
                else:
                    end_dt = parse(options['end_date'])
            options['end_date'] = tuple(map(int,
                end_dt.strftime("%Y,%m,%d").split(',')))
    else:
        end_dt = beg_dt + soon * oneday
        options['end_date'] = tuple(map(int,
            end_dt.strftime("%Y,%m,%d").split(',')))
    if 'cols' in options:
        if 'F' in options['cols']:
            # ignore other options
            options['cols'] = 'F'
        else:
            options['cols'] = keys2Nums(options['cols'])
            if type(options['cols']) == int:
                options['cols'] = (options['cols'],)
    else:
        options['cols'] = '((0,1,2),)'
    if 'details' in options:
        if options['details'] in [0, '0']:
            options['details'] = 0
        elif options['details'] in [1, '1']:
            options['details'] = 1
        elif options['details'] == '*':
            options['details'] = sort_str + u'I'
    else:
        options['details'] = 1
    return(options)


fieldNum = dict(
        y='0',      # y)ear
        m='1',      # m)onth
        d='2',      # d)ay
        s='3',      # s)ort num
        e='5',      # e)xtent minutes
        p='6',      # p)riority
        w='7',      # w)eek number (in year)
        q='8',      # q)uarter number
        c='9',      # c)ontext
        k1='10',    # k)eyword 1
        k2='11',    # k)eyword 2
        k3='12',    # k)eyword 3 and beyond
        l='13',     # l)ocation
        T='17',     # t)itle, description of item
        I='19',     # i)d, file name and lines
        u='21',     # u)ser
        P='22',     # p)roject name
        t='23',     # t)ag
        n='24',     # n)ote
        )


def keys2Nums(string):
    """
        Take a string in the format "((y,m,d),)" and convert it to a tuple
        of the form ((0,1,2),).
    """
    print('keys2Nums', string)
    if type(string) == tuple:
        return(string)
    try:
        for key in fieldNum:
            string = re.sub(key, fieldNum[key], string)
        print('string', string, type(string))
        cols = eval(string)
        return(cols)
    except:
        return((0,1,2),)

nameHash = {
        u'd' : 'day',
        u'b' : 'busy',
        u'p' : 'pastdue',
        u'n' : 'next',
        u'f' : 'folder',
        u'k' : 'keyword',
        u't' : 'tag',
        u'o' : 'outline',
        }

# TODO: make sure all this respects the calendar selection

filterKeys = {
        'search'    : ('_summary', 'd'),
        'context'   : ('c,'),
        'keyword'   : ('k',),
        'user'      : ('u',),
        'location'  : ('l',),
        'tag'       : ('t',),
        'path'      : ('fileinfo',)
        }


def setFilters(options):
    neg_fields = {}
    regex_fields = {}

    for field in ['search', 'context', 'keyword', 'user', 'location',
         'path']:
        if field in options and options[field]:
            if options[field][0] == '!':
                neg_fields[field] = True
                regex_fields[field] = re.compile(r'%s' %
                    options[field][1:], re.IGNORECASE)
            else:
                neg_fields[field] = False
                regex_fields[field] = re.compile(r'%s' %
                options[field],
                    re.IGNORECASE)
        else:
            neg_fields[field] = False
            regex_fields[field] = None
    regex_fields['tag'] = []
    if 'tag' in options and options['tag']:
        for tag in options['tag']:
            if tag[0] == '!':
                neg_tag = True
                if type(tag) == str:
                    regex_fields['tag'].append((neg_tag, re.compile(r'%s' %
                        tag[1:], re.IGNORECASE)))
                        #  tag[1:].decode(encoding), re.IGNORECASE)))
                else:
                    regex_fields['tag'].append((neg_tag, re.compile(r'%s' %
                        tag[1:], re.IGNORECASE)))
            else:
                neg_tag = False
                if type(tag) == str:
                    regex_fields['tag'].append((neg_tag, re.compile(r'%s' %
                        tag, re.IGNORECASE)))
                        #  tag.decode(encoding), re.IGNORECASE)))
                else:
                    regex_fields['tag'].append((neg_tag, re.compile(r'%s' %
                        tag, re.IGNORECASE)))
    return(neg_fields, regex_fields)

def filterTuple(tup, neg_fields, regex_fields, omit):
    # tup: (datetime.date, TypeNum, datetime.time, hsh)
    for field in ['search', 'context', 'keyword', 'user', 'location',
           'path']:
        if field in regex_fields and regex_fields[field]:
            s = " ".join([unicode(tup[-1][i])
                for i in filterKeys[field]])
            r = regex_fields[field].search(s)
            s_res = (r and r.group(0).strip())
            if (neg_fields[field] and s_res):
                return(False)
            if not neg_fields[field] and not s_res:
                return(False)
    if regex_fields['tag']:
        # this will be a list, each element must match
        t_res = False
        s = tup[-1]['t']
        tags = comma_regex.split(s)
        if tags:
            for neg_tag, tag_regex in regex_fields['tag']:
                for tag in tags:
                    r = tag_regex.search(tag)
                    t_res = (r and r.group(0).strip())
                    if t_res:
                        break
                if (neg_tag and t_res):
                    return(False)
                if not neg_tag and not t_res:
                    return(False)
    if omit:
        if omit[0] == '!':
            neg_omit = True
            omit = omit[1:]
        else:
            neg_omit = False
        nums = []
        for s in omit:
            if s in omitKeys:
                for i in omitKeys[s]:
                    nums.append(i)
        if neg_omit:
            if tup[1] not in nums: return(False)
        else:
            if tup[1] in nums: return(False)
    return(True)

def getMatchingTuples(tuples, options):
    if 'search' in options and options['search']:
        i1 = 0
        i2 = len(tuples)
    else:
        if 'begin_date' in options:
            i1 = bisect.bisect_left(tuples, options['begin_date'])
        else:
            i1 = None
        if 'end_date' in options:
            i2 = bisect.bisect_right(tuples, options['end_date'])
        else:
            i2 = None
    if i1 == i2:
        tups = []
    elif i1 and i2:
        tups = tuples[i1:i2]
    elif i1:
        tups = tuples[i1:]
    elif i2:
        tups = tuples[:i2]
    else:
        tups = tuples
    if 'omit' in options:
        omit = options['omit']
    else:
        omit = ''
    neg_fields, regex_fields = setFilters(options)
    matching = []
    busyTimes = {}
    for tup in tups:
        if filterTuple(tup, neg_fields, regex_fields, omit):
            matching.append(tup)
            if include_busy:
                if tup[3] == 1: # events with start time and extent
                    d_str = "%s-%s-%s" % tuple(tup[:3])
                    date = parse(d_str)
                    wd = int(date.strftime("%w"))
                    if not sundayfirst:
                        wd -= 1
                        if wd < 0:
                            wd = 6
                    # id, dy, sm, wd. sm, em
                    item = ((tup[19], tup[2], tup[4]), wd, tup[4], tup[4]+tup[5])
                    busyTimes.setdefault(tuple(tup[:3]), []).append(item)
    return(matching, neg_fields, regex_fields, busyTimes)

if __name__ == "__main__":
    s = "o -g ((y,m,d), k[:2])  -b '-1/1' -e '+1/1' -o !a"
    print(getOptsFromString(s))
    # print(getOpts(nameHash['o'], ['-h']))
    cols = keys2Nums("((y,m,d),)")
    print(cols, type(cols))
    # print("str:", s)
    # # l = s.split('-')
    # l = arg_regex.split(s)
    # head = l.pop(0).strip()
    # args = []
    # for x in l:
    #     if not len(x) > 1: continue
    #     args.extend(["-%s" % x[0], "%s" % x[1:].strip()])

    # print("args:", args)
    # o = get_opts(nameHash['o'], args)
    # print('type: "%s";' % head, 'opts:', o)
