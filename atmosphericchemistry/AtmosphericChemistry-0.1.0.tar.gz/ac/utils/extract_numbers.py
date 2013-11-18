"""Extract numbers from a string"""

import re


def extract_numbers(term):
    """Extract floating point numbers from a string and return them
    as list. Floating point numbers may begin with a digit or the decimal point
    and must include at least one digit. Numbers must not be preceeded by
    letters or the underscore character (these are assumed to be part of
    variable names). The routine uses a combination of regular expression and
    python string methods to achieve this."""
    # regex for detecting a float number:
    # r"(...)"  : group everything so that finditer will return it
    # [+\-]?    : zero or one sign (positive or negative)
    # (?:...)   : pseudo-group - pattern in parantheses belongs together but is not returned as group
    # (...|...) : alternative branches - number either starts with digit or with decimal point
    # \d+(.\d*)?: at least one digit before decimal point, then optional point and more digits
    # (\.\d+)+  : starts with decimal point and has at least one digit (must not be empty)
    # ([eE][+\-]?\d+) : optional exponential and finally at least one mandatory digit
    # Note that final digit may be all it gets!
    # Attempt to not match numbers after letters with (?<![a-zA-Z_]) fails, because this only
    # excludes the first digit after a letter. Therefore now add optional preceeding letter and
    # test_it afterwards if the match startswith letter (in which case it is ignored)
    pattern = re.compile(r"([a-zA-Z_]?[+\-]?(?:(?:\d+)(?:\.\d*)?|(?:\.\d+)+)(?:[eE][+\-]?\d+)?)")
    res = []
    matches = re.finditer(pattern, term)
    for m in matches:
        s = m.group()
        if not s:
            continue
        swalpha = s[0].isalpha() or s[0] == "_"           # startswith alpha
        fbsign = (s[1] == "-") or (s[1] == "+")           # followed by sign
        if swalpha and fbsign:
            res.append(s[1:])
        elif not swalpha:
            res.append(s)
    return res


