### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2013 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
import mimetypes
import os.path

# import Zope3 interfaces
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces

# import Zope3 packages
from zope.interface import classProvides

# import local packages
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class MIMETypesVocabulary(SimpleVocabulary):
    """MIME types vocabulary"""

    classProvides(IVocabularyFactory)

    def __init__(self, context):
        terms = (SimpleTerm(ext, ext, '%s (%s)' % (mimetype, ext)) for ext, mimetype in mimetypes.types_map.iteritems())
        super(MIMETypesVocabulary, self).__init__(sorted(terms, key=lambda x: x.title))


class MagicTypesVocabulary(SimpleVocabulary):
    """libmagic types vocabulary"""

    classProvides(IVocabularyFactory)

    def __init__(self, context):
        dirname, _filename = os.path.split(__file__)
        with open(os.path.join(dirname, 'magic', 'mime.types')) as f:
            terms = [SimpleTerm(mime, mime) for mime in f.read().split()]
        super(MagicTypesVocabulary, self).__init__(terms)
