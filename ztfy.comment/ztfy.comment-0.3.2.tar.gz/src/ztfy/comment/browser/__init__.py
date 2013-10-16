### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.comment.interfaces import IComments

# import Zope3 packages
from zope.publisher.browser import BrowserPage

# import local packages

from ztfy.comment import _


class CommentView(BrowserPage):

    def __call__(self):
        comments = IComments(self.context).getComments()
        return '\n\n'.join((self.getOutput(c) for c in comments))

    def getOutput(self, c):
        return """Date: %s
                  Principal: %s
                  Body: %s
                  Tags: %s""" % (c.date,
                                 c.principal_id,
                                 c.body,
                                 c.tags)
