##############################################################################
#
# Copyright (c) 2013 Christopher Lozinski (lozinski@freerecruiting.com).
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
"""ZPT Page Content Component Interfaces
"""
from zope.schema import SourceText, Bool, TextLine
from zope.interface import Interface

class IZopachePageTemplate(Interface):
    "Zopache Page Templates are a persistent implementation of Page Templates."


    def setSource(text, content_type='text/html'):
        """Save the source of the page template.

        'text' must be Unicode.
        """

    def getSource():
        """Get the source of the page template."""

    source = SourceText(
        title=u"Source",
        description=u"The source of the page template.",
        required=True)

    expand = Bool(
        title=u"Expand macros when editing",
        description=u"Expand macros so that they all are shown in the code.",
        default=False,
        required=True)

    evaluateInlineCode = Bool(
        title=u"Evaluate Inline Code",
        description=u"Evaluate code snippets in TAL.",
        default=False,
        required=True)


class IRenderZopachePageTemplate(Interface):

    content_type = TextLine(
        title=u"Content Type",
        description=u"Content type of generated output",
        default=u"text/html",
        required=True)

    def render(request, *args, **kw):
        """Render the page template.

        The first argument is bound to the top-level 'request'
        variable. The positional arguments are bound to the 'args'
        variable and the keyword arguments are bound to the 'options'
        variable.
        """

