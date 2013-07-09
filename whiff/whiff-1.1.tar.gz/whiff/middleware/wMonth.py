"""
support for creating ajaxy calendar objects
"""

skipWhiffDoc = "I'm not sure this one is a keeper"

import calendar

class Month:
    def __init__(self, prefix, yearNumber, monthNumber, focusDay):
        startDay = 0 # XXX someday carefully allow startday to be 6 (sunday)
        self.prefix = prefix
        self.year = yearNumber
        self.month = monthNumber
        self.start = startDay
        self.focusDay = focusDay
        self.focusDict = None
        self.weekAndDayToDict = {}
        c = calendar.Calendar(startDay)
        weekcount = 0
        self.allDicts = []
        for weekdates in c.monthdatescalendar(self.year, self.month):
            daycount = 0
            for daydate in weekdates:
                if daydate.month==monthNumber:
                    D = {}
                    D["date"] = daydate
                    dayNumber = daydate.day
                    D["id"] = "%s_%s_%s_%s" % (prefix, yearNumber, monthNumber, dayNumber)
                    D["value"] = self.value(daydate)
                    D["week"] = weekcount
                    D["weekday"] = daycount
                    self.weekAndDayToDict[ (weekcount, daycount) ] = D
                    self.allDicts.append(D)
                    if dayNumber==focusDay:
                        self.focusDict = D
                daycount+=1
            weekcount+=1
    def dictBindings(self, D, upDefault, downDefault, leftDefault, rightDefault):
        id = D["id"]
        v = D["value"]
        week = D["week"]
        day = D["weekday"]
        up = upDefault
        down = downDefault
        left = leftDefault
        right = rightDefault
        upD = self.weekAndDayToDict.get( (week-1, day) )
        if upD:
            up = upD["id"]
        downD = self.weekAndDayToDict.get( (week+1, day) )
        if downD:
            down = downD["id"]
        leftD = self.weekAndDayToDict.get( (week, day-1) )
        if leftD:
            left = leftD["id"]
        rightD = self.weekAndDayToDict.get( (week, day+1) )
        if rightD:
            right = rightD["id"]
        fmt = '{"id": "%s", "v": "%s", "u": "%s", "d": "%s", "r": "%s",  "l": "%s"}' % (
            id, v, up, down, right, left)
        return fmt
    def jsBindings(self, upDefault, downDefault, leftDefault, rightDefault):
        L = self.jsBindingsGen(upDefault, downDefault, leftDefault, rightDefault)
        return "".join(L)
    def firstId(self):
        return self.allDicts[0]["id"]
    def lastId(self):
        return self.allDicts[-1]["id"]
    def jsBindingsGen(self, upDefault, downDefault, leftDefault, rightDefault):
        inside = False
        #yield "[\n"
        if self.focusDict:
            yield self.dictBindings(self.focusDict, upDefault, downDefault, leftDefault, rightDefault)
            inside = True
        for week in self.weekrange():
            for day in range(7):
                D = self.weekAndDayToDict.get( (week, day) )
                if D is not None:
                    if inside:
                        yield ",\n"
                    else:
                        yield "\n"
                    fmt = self.dictBindings(D,  upDefault, downDefault, leftDefault, rightDefault)
                    yield fmt
                    inside = True
        #yield "\n]"
    def value(self, date):
        "for possible overloading -- the presentation of a date"
        return str(date)
    def weekrange(self):
        wds = self.weekAndDayToDict.keys()
        weeks = [wd[0] for wd in wds]
        maxweek = max(weeks)
        return range(maxweek+1)
    def preformattedGen(self, cssclass=None, complete=False):
        if complete:
            yield "<pre>\n"
        yield calendar.weekheader(4)+"\n"
        for week in self.weekrange():
            for day in range(7):
                D = self.weekAndDayToDict.get( (week, day) )
                if D is None:
                    yield "     "
                else:
                    dayOfMonth = D["date"].day
                    formatted= " %2d  " % dayOfMonth
                    if cssclass:
                        formatted = '<span id="%s" class="%s">%s</span>' % (D["id"], cssclass, formatted)
                    yield formatted
            yield "\n"
        if complete:
            yield "</pre>\n"
    def preformatted(self, cssclass=None):
        L = list(self.preformattedGen(cssclass))
        return "".join(L)

def test0():
    m = Month("prefix", 2009, 2, 11)
    print "test preformatting<br>"
    print "<pre>"
    print m.preformatted()
    print "</pre>"
    print
    print "with css spans:"
    print "<pre>"
    print m.preformatted("cssclassname")
    print "</pre>"
    print
    print "javascript bindings"
    print "<pre> ["
    print m.jsBindings("UPPER", "LOWER", "LEFTISH", "RIGHTISH")
    print "] </pre>"

def test1():
    m = Month("prefix", 2009, 2, 11)
    print """

{{env
        whiff.content_type: "text/html",
        whiff.filter: false 
        /}}

        <html>
        <head>
        <title> month test </title>

        <script>

    function alertaction(s) {
        function go() {
           alert(s);
        };
        return go;
    }

    """

    print "Bindings = ["+m.jsBindings("UPPER", "LOWER", "LEFTISH", "RIGHTISH")
    # add bindings for default anchors
    id1 = m.firstId()
    idn = m.lastId()
    print ', {"id": "UPPER", "v": "(up)",  "u": "%s", "d": "%s", "r":"%s", "l": "%s", "action": alertaction("UP")}' % ("LOWER", id1, id1, idn)
    print ', {"id": "LOWER", "v": "(down)",  "u": "%s", "d": "%s", "r":"%s", "l": "%s", "action": alertaction("DOWN")}' % (idn, "UPPER", id1, idn)
    print ', {"id": "LEFTISH", "v": "(left)",  "u": "%s", "d": "%s", "r":"%s", "l": "%s", "action": alertaction("LEFT")}' % (idn, id1, id1, "RIGHTISH") 
    print ', {"id": "RIGHTISH", "v": "(right)",  "u": "%s", "d": "%s", "r":"%s", "l": "%s", "action": alertaction("RIGHT")}' % (id1, idn, "LEFTISH", id1)
    print "];"
    print """

    {{include "whiff_middleware/completions.js"/}}

    </script>

    <style type="text/css">
    {{include "whiff_middleware/completions.css"/}}
    </style>

    </head>
    <body>

    <hr>
    <div id="debugDiv">Debug area</div>

    <form name="test">
    <br>name: <input name="name">
    <br>input: <input autocomplete="off" name="testInput" id="testInput" type="text"
                    onfocus="jswhiff_bindSuggestions('testInput','suggestions','preview', Bindings, true, 'debugDiv')" >
    <br>
    other name: <input name="othername">

    <div id="suggestions" class="jswhiff_suggestion" style="width:400px">
    <table>
    <tr>
    <td width="33%" align="left"> <span id="LEFTISH" class="jswhiff_suggestionItem">left</span></td>
    <td width="33%" align="center"> <span id="UPPER" class="jswhiff_suggestionItem">up</span> </td>
    <td width="33%" align="right"> <span id="RIGHTISH" class="jswhiff_suggestionItem">right</span>  </td>
    <tr>
    <th colspan="3"> February 2009 </th>
    </tr>
    <tr>
    <td colspan="3" align="center">
    """
    print "<pre>"
    print m.preformatted("jswhiff_suggestionItem")
    print """</pre>
    <span id="LOWER" class="jswhiff_suggestionItem">down</span> <br>
    [TAB]: <span id="preview">N/A</span>
    </td>
    </tr>
    </table>
    </div>

    </form>

    </body>
    </html>
    """

if __name__=="__main__":
    test1()
