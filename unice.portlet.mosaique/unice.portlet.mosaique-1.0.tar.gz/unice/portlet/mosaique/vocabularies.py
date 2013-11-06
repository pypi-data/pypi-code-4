# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from unice.portlet.mosaique import MosaiquePortletMessageFactory as _


class ItemDisplayVocabulary(object):
    """Vocabulary factory for item_display.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary(
            [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                for pair in [
                    (u'title', _(u'Titre')),
                    (u'desc', _(u'Description')),
                    (u'date', _(u'Date')),
                    (u'location', _(u'Lieu')),
            ]]
        )
ItemDisplayVocabularyFactory = ItemDisplayVocabulary()
