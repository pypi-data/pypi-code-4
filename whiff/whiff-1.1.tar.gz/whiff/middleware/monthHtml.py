whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/monthHtml - generate a month popup
{{/include}}

The <code>whiff_middleware/monthHtml</code>
middleware 
returns HTML content for a month popup.  This middleware is deprecated,
please use jscript instead.
"""

whiffCategory = "tools"

import time
import calendar

# imports must be absolute
from whiff.middleware import misc
from whiff.middleware import wMonth

def fixMDY(month, day, year):
    #pr "fixmdy", (month,day,year)
    if year is None:
        lt = time.localtime()
        year = lt[0]
        if month is None:
            month = lt[1]
            if day is None:
                day = lt[2]
    elif month is None:
        month = 1
    if month<1:
        month = 12
        year -= 1
        #pr "back to year", month,year
    if month>12:
        month = 1
        year += 1
        #pr "forward to year", month,year
    return (month, day, year)

class MonthHtml(misc.utility):
    def __init__(self,
                 prefix="",
                 year=None,
                 month=None,
                 day=None,
                 style="jswhiff_suggestionItem",
                 ):
        self.prefix = prefix
        self.year = year
        self.month = month
        self.day = day
        self.style = style
    def __call__(self, env, start_response):
        prefix = self.param_value(self.prefix, env)
        year = self.param_json(self.year, env)
        month = self.param_json(self.month, env)
        day = self.param_json(self.day, env)
        style = self.param_value(self.style, env)
        (month, day, year) = fixMDY(month, day, year)
        M = wMonth.Month(prefix, year, month, day)
        month_name = calendar.month_name[month]
        start_response("200 OK", [('Content-Type', 'text/html')])
        yield "<table>\n"
        yield '<tr> <td id="%s_disable" colspan="3" align="right" class="%s">&#215;</td> </tr>' % (prefix, style)
        yield "<tr>\n"
        yield '<td width="33%"'
        yield ' align="left" id="%s_previous" class="%s">&lt;&lt;</span></td>\n' % (prefix, style)
        yield '<td width="33%"'
        yield ' align="left"> <span class="%s">%s %s</span></td>\n' % (style, month_name, year)
        yield '<td width="33%"'
        yield ' align="right" id="%s_next" class="%s">&gt;&gt;</span></td>\n' % (prefix, style)
        yield "</tr>\n"
        yield "<tr>\n"
        yield '<td colspan="3" align="center">\n'
        yield "<pre>\n"
        yield M.preformatted(style)
        yield "</pre>\n"
        yield "</td>\n"
        yield "</tr>\n"
        yield "</table>\n"

__middleware__ = MonthHtml

def test():
    M = MonthHtml("xxx", 2009, 2, 11)
    L = M({}, misc.ignore)
    T = "".join(list(L))
    print "test output"
    print T

if __name__=="__main__":
    test()
