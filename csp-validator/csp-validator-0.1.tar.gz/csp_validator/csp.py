# -*- coding: utf-8 -*-
import re

import parsimonious
from parsimonious.grammar import Grammar

# grammar matches a single CSP rule such as 'default-src *'
# Users can fit the entire CSP header into validate(..)
# function. One can easily add a + regex around policy to
# match the entire CSP header. But for better error reporting,
# I recommend keeping the grammar single pass instead of a loop.
uri = r'(http://|https://|\*\.)?' + \
      r'([a-z0-9][-a-z0-9]+)(\.[a-z0-9][-a-z0-9]+)+(:\d+)?'
grammar = Grammar(
    """
    policy = directive_name space (directive_value (space directive_value)*) semicolon?
    directive_name = "default-src" / "script-src" / "img-src"
    directive_value = "*" / "'none'" / "'self'" / "https:" / uri
    space = " "
    semicolon = ";"
    uri = ~"%s"
    """ % uri)

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
    """
    We have to either fail or warn a CSP rule if they have the
    following issues:

    (1) when 'none' or * is found as a directive value, having
    other directive values defined in the grammar appear
    in the same policy (per directive), and/or
    (2) when 'unsafe-inline' or 'unsafe-eval' is found as part of
    a policy (per directive)

    If the policy passes the grammar test, we can only assume it
    works.

    If the policy does not pass the grammar test, defer the
    exception until later; add the error to a list.

    If the policy contains 'unsafe-inline' or 'unsaife-eval',
    ddd the policy to warning.

    """

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
            check(rule)
        except parsimonious.exceptions.ParseError as e:
            # do a little parsing for better error report
            error = repr(e).split("didn't match at ")
            if len(error) >=2:
                error = error[1].strip('.') # remove ending period symbol
            else:
                error = repr(e).split("begins with ")[1].strip('.') # remove ending period symbol
            errors.append((rule, "%s does not match CSP grammar." % error))
        except CSPRuleWarning as e:
            warnings.append((rule, e.msg))

    # if rules is None, well, we got an empty string :)
    return rules, warnings, errors

def check(rule):
    """ Perform some quick check on each rule in the CSP header. """
    # split incoming rule into a list by space, which produce
    # [directive_name, directive_value1, directive_value2, etc]
    parts = rule.split()
    if parts:   # if rule ends with ; we get an empty as last item
        # parts[0] should be a directive name
        # parts[1:] should be directive value
        for part in parts:
            if part in ('unsafe-inline', 'unsafe-eval'):
                raise CSPRuleWarning(rule, "%s is detectd." % part)
            elif part in ("'none'", "*") and len(parts) > 2:
                raise CSPRuleWarning(rule, "When %s is present, other values cannot be present as well." % part)
            elif part in ("inline-script", "inline-eval"):
                eqv = {'inline-script': 'unsafe-inline', 'inline-eval': 'unsafe-eval'}
                raise CSPRuleWarning(rule, \
                    "%s is deprecated in favor of the W3C specification. Use %s instead." %(part, eqv[part]))
