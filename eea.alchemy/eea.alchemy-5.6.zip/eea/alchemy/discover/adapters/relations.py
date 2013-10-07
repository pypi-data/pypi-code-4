""" Auto-discover relatedItems
"""
import logging
from zope.interface import implements
from zope.component import getUtility
from zope.component.hooks import getSite
from plone.uuid.interfaces import IUUID
from eea.alchemy.interfaces import IDiscoverRelatedItems
from eea.alchemy.interfaces import IDiscoverUtility
from eea.alchemy.config import EEAMessageFactory as _
from eea.alchemy.discover.adapters import Discover
from eea.alchemy.relations import canRelate
logger = logging.getLogger('eea.alchemy')


class DiscoverRelatedItems(Discover):
    """ Common adapter to auto-discover related items in context metadata
    """
    implements(IDiscoverRelatedItems)
    title = _(u'Related items')

    def __init__(self, context):
        super(DiscoverRelatedItems, self).__init__(context)
        self.field = 'relatedItems'
        self.index = 'relatedItems'
        self._tags = []

    @property
    def preview(self):
        """ Discovery preview
        """
        doc = self.context
        # ZCatalog brain
        if getattr(doc, 'getObject', None):
            doc = doc.getObject()

        field = doc.getField(self.field)
        if not field:
            logger.warn('%s has no %s schema field. %s not set',
                        doc.absolute_url(1), self.field, self.title)
            return

        languageIndependent = getattr(field, 'languageIndependent', False)
        isCanonical = getattr(doc, 'isCanonical', None)
        isTranslation = not isCanonical() if isCanonical else False
        if languageIndependent and isTranslation:
            return

        mutator = field.getMutator(doc)
        if not mutator:
            logger.warn("Can't edit field %s for doc %s",
                        self.field, doc.absolute_url(1))
            return

        current = [IUUID(obj, None) for obj in field.getAccessor(doc)()]
        tags = [tag.get('text') for tag in self.tags]

        if not set(tags).difference(current):
            return

        # Preserve current tags
        for tag in current:
            if tag not in tags:
                tags.append(tag)

        return (tags, 'Update %s for %s. Before: %s, After: %s' %
                (self.field, doc.absolute_url(1), current, tags))

    @property
    def tags(self):
        """ Getter
        """
        doc = self.context
        getObject = getattr(doc, 'getObject', None)
        string = ""
        for prop in self.metadata:
            text = ''

            # ZCatalog brain
            if getObject:
                text = getattr(doc, prop, '')
                if not text:
                    doc = getObject()

            # ATContentType
            if not text and getattr(doc, 'getField', None):
                field = doc.getField(prop)
                if not field:
                    continue
                text = field.getAccessor(doc)()

            if not text:
                continue

            if not isinstance(text, (unicode, str)):
                continue

            string += '\n' + text

        discover = getUtility(IDiscoverUtility, name=u'links')
        if not discover:
            return

        string = string.strip()
        if not string:
            return

        site = getSite().absolute_url()
        if getObject:
            doc = getObject()

        myuid = IUUID(doc, None)
        discovered = []
        try:
            discovered = list(discover(string, match=site))
        except Exception, err:
            logger.exception("%s while discovering items on: %s",
                            err, doc.absolute_url_path())

        for item in discovered:
            text = item.get('text')
            if text.startswith('resolveuid/'):
                uid = text.split('/')[1]
                if uid == myuid:
                    continue

                if canRelate(doc, uid=uid):
                    item['text'] = uid
                    yield item
                    continue

            try:
                obj = doc.unrestrictedTraverse(text)
            except Exception, err:
                logger.exception("%s while trying " + \
                                "doc.unrestrictedTraverse(text)" + \
                                "with doc: %s    text: %s",
                                err, doc.absolute_url_path(), text)
                continue
            else:
                if not canRelate(doc, obj):
                    continue

                uid = IUUID(obj, None)
                if not uid:
                    continue

                if uid == myuid:
                    continue
                item['text'] = uid
                yield item
                continue

    @tags.setter
    def tags(self, value):
        """ Setter
        """
        data = self.preview
        if not data:
            return

        tags, info = data

        doc = self.context
        if getattr(doc, 'getObject', None):
            # ZCatalog brain
            doc = doc.getObject()

        field = doc.getField(self.field)
        mutator = field.getMutator(doc)

        logger.info(info)

        mutator(tags)
        doc.reindexObject(idxs=[self.index])
