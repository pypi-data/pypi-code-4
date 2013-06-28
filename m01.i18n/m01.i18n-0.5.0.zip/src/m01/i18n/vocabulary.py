##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
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
"""
$Id: vocabulary.py 3736 2013-06-08 01:04:40Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from m01.i18n import interfaces


class AvailableLanguagesVocabulary(SimpleVocabulary):
    """A vocabular of available languages from the context object."""

    zope.interface.implements(interfaces.IAvailableLanguagesVocabulary)

    zope.interface.classProvides(IVocabularyFactory)

    def __init__(self, context):
        terms = []
        
        # returns available languages form the object itself
        # but just after creation of the object
        try:
            languages = context.getAvailableLanguages()
        except AttributeError:
            languages = []

        for lang in languages:
            terms.append(SimpleTerm(lang, lang, lang))

        terms.sort(lambda lhs, rhs: cmp(lhs.title, rhs.title))
        super(AvailableLanguagesVocabulary, self).__init__(terms)
