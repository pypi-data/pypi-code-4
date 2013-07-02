# -*- coding: utf-8 -*-
import re

import parsimonious
from parsimonious.grammar import Grammar

# grammar matches a single CSP rule such as 'default-src *'
# Users can fit the entire CSP header into validate(..)
# function. One can easily add a + regex around policy to
# match the entire CSP header. But for better error reporting,
# I recommend keeping the grammar single pass instead of a loop.


uri = r'([a-z0-9][-a-z0-9]+)(\.[a-z0-9][-a-z0-9]+)+(:\d+)?'

grammar = Grammar(
    """
    policy = (space* directive_name ((space "'none'" semicolon?)  / ((space directive_value)+ semicolon?)))+
    directive_name = "default-src" / "script-src" / "object-src" / "style-src" / "img-src" / "media-src" / "frame-src" / "font-src" /
"connect-src" / "sandbox" / "report-uri"
    directive_value = keyword_source / host_source / scheme_source
    scheme = "https" / "http" / "ftp" / "data"
    scheme_source = (scheme ":")
    host_source = (scheme? "://"? host port?)
    port = ~"[0=9]"+
    host = ("*."? host_char+ ("." host_char+)*) / "*"
    host_char = ~"[-a-z0-9]"
    keyword_source = "'self'" / "'unsafe-inline'" / "'unsafe-eval'" / "'inline-script'" / "'inline-eval'"
    space = " "
    semicolon = ";"
""")

def parse(input):
    return grammar.parse(input)

class CSPRuleWarning(Warning):
    def __init__(self, rule, msg):
        super(CSPRuleWarning, self).__init__()
        self.msg = msg
        self.rule = rule

    def __str__(self):
        return repr("CSP rule: %s\n Issue: %s" %(self.rule, self.msg))

def validate(csp):
    warnings = []
    errors = []
    p = re.compile(r";\s*")
    # the csp rules are split by the pattern into a list
    # ['default-src *', 'img-src *.example.org']
    rules = p.split(csp)
    # go through each rule, and split each rule in the list by space
    # each split should produce (directive_name, directive_value, ...)
    for rule in rules:
        try:
            parse(rule)
            warns = check(rule)
            if warns:
                warnings.append( (rule, warns) )
        except parsimonious.exceptions.ParseError as e:
            # do a little parsing for better error report
            error = repr(e).split("didn't match at ")
            if len(error) >=2:
                error = error[1].strip('.') # remove ending period symbol
            else:
                error = repr(e).split("begins with ")[1].strip('.') # remove ending period symbol
            errors.append((rule, "%s does not match CSP grammar." % error))        

    # if rules is None, well, we got an empty string :)
    if rules:
        rules = filter(None, rules) # remove empty item in the list
    return rules, warnings, errors

def check(rule):
    """ Perform some quick check on each rule in the CSP header. """
    check_warnings = []
    # split incoming rule into a list by space, which produce
    # [directive_name, directive_value1, directive_value2, etc]
    parts = rule.split()
    if parts:   # if rule ends with ; we get an empty as last item
        # parts[0] should be a directive name
        # parts[1:] should be directive value
        for part in parts:
            if part in ("'unsafe-inline'", "'unsafe-eval'"):
                check_warnings.append("Enabling %s can enable cross-site scripting vulnerabilities." % part)
            elif part in ("'inline-script'", "'inline-eval'"):
                # suggest the new syntax
                eqv = {"'inline-script'": "'unsafe-inline'", "'inline-eval'": "'unsafe-eval'"}
                check_warnings.append(
                    "%s is deprecated in favor of the W3C specification; use %s instead." %(part, eqv[part]))

    return check_warnings
