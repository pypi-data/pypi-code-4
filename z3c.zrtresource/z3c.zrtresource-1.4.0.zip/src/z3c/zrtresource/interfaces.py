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
"""Templated Resource Interfaces

$Id$
"""
__docformat__='restructuredtext'

import zope.interface
import zope.schema
import zope.component.interfaces


class UnknownZRTCommand(ValueError):
    """An unknown ZRT Command was specified"""


class ArgumentError(ValueError):
    """Error while parsing the command arguments."""


class IZRTProcessor(zope.interface.Interface):
    """ZRT Processor"""

    source = zope.schema.Bytes(
        title=u'Source',
        description=u'The source of the expression.')

    def compile():
        """Compile the source to binary form."""

    def process(context, request):
        """Process the source with given context and request.

        Return the result string.
        """


class IZRTCommand(zope.interface.Interface):
    """A ZRT command"""

    isAvailable = zope.schema.Bool(
        title=u'Is Available',
        description=u'Tell whether the command is still available.')

    def process(text, context, request):
        """Process the given text with given context and request.

        Return the result string.
        """

class IZRTCommandFactory(zope.component.interfaces.IFactory):
    """ factory for IZRTCommand """


class IZRTExpression(zope.interface.Interface):
    """An expression to be used in a command."""

    source = zope.schema.Bytes(
        title=u'Source',
        description=u'The source of the expression.')

    context = zope.schema.Object(
        title=u'Context',
        description=u'Context of the template, usually a site.',
        schema=zope.interface.Interface)

    request = zope.schema.Object(
        title=u'Request',
        description=u'Request of the template, usually a site.',
        schema=zope.interface.Interface)


class IZRTInputExpression(IZRTExpression):

    def process(text, outputExpr):
        """Evaluate the expression and update the """


class IZRTOutputExpression(IZRTExpression):

    def process(**kw):
        """Process the expression and return the output string.

        The keyword arguments are additional namespaces.
        """
