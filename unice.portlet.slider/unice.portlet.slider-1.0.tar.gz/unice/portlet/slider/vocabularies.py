# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from unice.portlet.slider import SliderPortletMessageFactory as _


class ItemDisplayVocabulary(object):
    """Vocabulary factory for item_display.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary(
            [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                for pair in [
                    (u'captions', _(u'Légende')),
                    (u'captions_desc', _(u'Description dans la légende')),
                    (u'captions_date', _(u'Date dans la légende')),
                    (u'pager', _(u'Pagination')),
                    (u'auto', _(u'Démarrage automatique')),
            ]]
        )
ItemDisplayVocabularyFactory = ItemDisplayVocabulary()
