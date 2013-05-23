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
"""Python Script Component Interfaces
"""
from zope.schema import SourceText, TextLine
from zope.interface import Interface

class IPythonScript(Interface):
    "Expose Python functions as TTW content type."

    signature = TextLine(
        title=u"Signature",
        description=u"The signature of the function.",
        required=True)

    source = SourceText(
        title=u"Source",
        description=u"The source of the page template.",
        required=True)

    def __call__(*args, **kw):
        """Evaluate the Python Script.

        The return value of the function is returned.
        """
