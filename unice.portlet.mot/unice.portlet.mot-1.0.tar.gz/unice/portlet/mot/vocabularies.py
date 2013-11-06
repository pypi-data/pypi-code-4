# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from unice.portlet.mot import MotPortletMessageFactory as _


class ItemDisplayVocabulary(object):
    """Vocabulary factory for item_display.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary(
            [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                for pair in [
                    (u'date', _(u'Date')),
                    (u'image', _(u'Image')),
                    (u'description', _(u'Description')),
                    (u'body', _(u'Body')),
            ]]
        )
ItemDisplayVocabularyFactory = ItemDisplayVocabulary()
