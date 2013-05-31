##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Templated Resource Processor

$Id$
"""
__docformat__='restructuredtext'
import re
import zope.interface
from zope.pagetemplate import engine
from z3c.zrtresource import interfaces

# <EXPR-TYPE>"<INPUT-EXPR>" <EXPR-TYPE>"<OUTPUT-EXPR>" <NUM>
NAME = r'[a-zA-Z0-9_-]*'
ARGS_REGEX = re.compile(r' *(%s)"([^"]*)" *(%s)"([^"]*)" *([0-9]*)' %(NAME, NAME))


class BaseExpression(object):

    def __init__(self, source, context, request):
        self.source = source
        self.context = context
        self.request = request


class StringInputExpression(BaseExpression):
    """A simple string input expression"""
    zope.interface.implements(interfaces.IZRTInputExpression)

    def process(self, text, outputExpr, count=None):
        regex = re.compile(re.escape(self.source))
        return regex.subn(outputExpr.process(), text, count or 0)


class StringOutputExpression(BaseExpression):
    """A simple string input expression"""
    zope.interface.implements(interfaces.IZRTOutputExpression)

    def process(self, **kw):
        # Ignore any keyword arguments, since this is static replacement
        return self.source


class RegexInputExpression(BaseExpression):
    """A regex string input expression"""
    zope.interface.implements(interfaces.IZRTInputExpression)

    def process(self, text, outputExpr, count=None):
        regex = re.compile(self.source)
        return regex.subn(outputExpr.process(), text, count or 0)


class TALESOutputExpression(BaseExpression):
    """A simple string input expression"""
    zope.interface.implements(interfaces.IZRTOutputExpression)

    def process(self, **kw):
        expr = engine.TrustedEngine.compile(self.source)
        kw.update({'context': self.context, 'request': self.request})
        econtext = engine.TrustedEngine.getContext(kw)
        return expr(econtext)


class Replace(object):
    """A ZRT Command to replace sub-strings of the text"""
    zope.interface.implements(interfaces.IZRTCommand)

    inputExpressions = {
        '': StringInputExpression,
        'str': StringInputExpression,
        're': RegexInputExpression,
        }

    outputExpressions = {
        '': StringOutputExpression,
        'str': StringOutputExpression,
        'tal': TALESOutputExpression,
        }

    def __init__(self, args, start, end):
        self.start = start
        self.end = end
        self.processArguments(args)

    @property
    def isAvailable(self):
        return self.num is None or self.num > 0

    def processArguments(self, args):
        match = ARGS_REGEX.match(args)
        if match is None:
            raise interfaces.ArgumentError(args)

        self.itype, self.input, self.otype, self.output, self.num = match.groups()
        self.num = self.num and int(self.num) or None

        if self.itype not in self.inputExpressions:
            raise ValueError(self.itype)

        if self.otype not in self.outputExpressions:
            raise ValueError(self.otype)

    def process(self, text, context, request):
        iexpr = self.inputExpressions[self.itype](
            self.input, context, request)
        oexpr = self.outputExpressions[self.otype](
            self.output, context, request)
        text, num = iexpr.process(text, oexpr, self.num)
        if self.num is not None:
            self.num -= num
        return text
