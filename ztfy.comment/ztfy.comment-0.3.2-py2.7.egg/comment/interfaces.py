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
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.security.interfaces import IPrincipal

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.interface.common.sequence import IReadSequence, IWriteSequence
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema import Datetime, Object, Choice, Set

# import local packages
from schema import CommentField
from ztfy.security.schema import Principal

from ztfy.comment import _


class ICommentable(IAttributeAnnotatable):
    """Marker interface for commentable contents"""


class IComment(ICommentable):
    """Base class for comments"""

    date = Datetime(title=_("Creation date"),
                    description=_("Date and time of comment creation"),
                    required=True,
                    readonly=True)

    principal_id = Principal(title=_("Creation principal"),
                             description=_("The ID of the principal who added this comment"),
                             required=True,
                             readonly=True)

    principal = Object(schema=IPrincipal,
                       title=_("Comment creator"),
                       description=_("Principal who added the comment"),
                       required=True,
                       readonly=True)

    body = CommentField(title=_("Comment body"),
                        description=_("Main content of this comment"),
                        required=True)

    body_renderer = Choice(title=_("Comment renderer"),
                           description=_("Name of utility used to render comment's body"),
                           required=True,
                           vocabulary='SourceTypes',
                           default=u'zope.source.plaintext')

    in_reply_to = Object(title=_("Comment's parent"),
                         description=_("Previous comment to which this comment replies"),
                         required=False,
                         schema=ICommentable)

    tags = Set(title=_("Comment tags"),
               description=_("A list of internal tags used to classify comments"),
               required=False)

    def getAge():
        """Return comment age"""

    def render(request=None):
        """Render comment body"""


class ICommentsListReader(IReadSequence):
    """Base class reader for comments"""


class ICommentsListWriter(IWriteSequence):
    """Base class writer for comments"""


class ICommentsList(IReadSequence, IWriteSequence):
    """Main class for comments list"""


class ICommentsReader(Interface):
    """Main reader class for comments"""

    def getComments(tag=None):
        """Get comments list"""


class ICommentsWriter(Interface):
    """Main writer class for comments"""

    def addComment(body, in_reply_to=None, renderer=None, tags=None):
        """Add a new comment"""


class IComments(ICommentsReader, ICommentsWriter):
    """Main class for comments"""


class ICommentAddedEvent(IObjectModifiedEvent):
    """Marker interface for comment added events"""

    comment = Object(title=_("Added comment"),
                     description=_("The comment object which was added"),
                     required=True,
                     schema=IComment)
