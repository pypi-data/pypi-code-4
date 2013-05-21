""" Auto-discover keywords
"""
import logging
from zope.interface import implements
from zope.component import getUtility, queryAdapter
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from eea.alchemy.interfaces import IDiscoverTags
from eea.alchemy.interfaces import IDiscoverKeywords
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
logger = logging.getLogger('eea.alchemy.discover')

class DiscoverTags(object):
    """ Common adapter to auto-discover keywords in context metadata
    """
    implements(IDiscoverTags)

    def __init__(self, context):
        self.context = context
        self._key = None
        self.field = 'subject'
        self._metadata = ('title', 'description')

    @property
    def key(self):
        """ AlchemyAPI key
        """
        if self._key is not None:
            return self._key

        site = getSite()
        settings = queryAdapter(site, IAlchemySettings)
        self._key = settings.token
        if not self._key:
            logger.exception(
                'AlchemyAPI key not set in Site Setup > Alchemy Settings')
            return self._key
        return self._key

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
            logger.warn('%s has no %s schema field. Keywords not set',
                        doc.absolute_url(1), self.field)
            return

        mutator = field.getMutator(doc)
        if not mutator:
            logger.warn("Can't edit field %s for doc %s",
                        self.field, doc.absolute_url(1))
            return

        tags = set(tag.get('text') for tag in self.tags)
        current = field.getAccessor(doc)()
        if isinstance(current, (str, unicode)):
            current = (current,)

        duplicates = set()
        for tag in tags:
            if isinstance(tag, str):
                tag = tag.decode('utf-8')
            duplicates.add(tag.lower())

        for tag in current:
            if isinstance(tag, str):
                tag = tag.decode('utf-8')
            lower = tag.lower()
            if lower in duplicates:
                continue

            tags.add(tag)
            duplicates.add(lower)

        if not set(tag.lower() for tag in tags).difference(
            set(tag.lower() for tag in current)):
            return

        tags = list(tags)
        tags.sort()
        tags = tuple(tags)

        return (tags, 'Update %s for %s.\n Before: %s \n After:  %s' %
                         (self.field, doc.absolute_url(1), current, tags))

    @property
    def existing(self):
        """ Get existing keywords from ZCatalog
        """
        ctool = getToolByName(self.context, 'portal_catalog')
        index = ctool.Indexes.get('Subject', None)
        if not index:
            return
        for value in index.uniqueValues():
            yield value

    def getMetadata(self):
        """ Getter
        """
        return self._metadata

    def setMetadata(self, value):
        """ Setter
        """
        if isinstance(value, (str, unicode)):
            value = (value,)
        self._metadata = value

    metadata = property(getMetadata, setMetadata)

    def getTags(self):
        """ Getter
        """
        string = ""
        for prop in self.metadata:
            if getattr(self.context, 'getField', None):
                # ATContentType
                field = self.context.getField(prop)
                if not field:
                    continue
                text = field.getAccessor(self.context)()
            else:
                # ZCatalog brain
                text = getattr(self.context, prop, '')

            if not text:
                continue

            if not isinstance(text, (unicode, str)):
                continue

            if isinstance(text, unicode):
                text = text.encode('utf-8')

            string += '\n' + text

        string = string.strip()
        if not string:
            return

        discover = getUtility(IDiscoverKeywords)
        duplicates = set()
        items = discover(self.key, string)
        for item in items:
            keyword = item.get('text')
            if not isinstance(keyword, unicode):
                keyword = keyword.decode('utf-8')
                item['text'] = keyword

            keyword = keyword.lower()
            if keyword in duplicates:
                continue

            duplicates.add(keyword)
            yield item

        # Search in portal_catalog existing keywords
        for keyword in self.existing:
            if isinstance(keyword, str):
                keyword = keyword.decode('utf-8')

            lower = keyword.lower()
            if lower in duplicates:
                continue
            if lower not in string.decode('utf-8').lower():
                continue

            duplicates.add(lower)
            yield {
                'relevance': '100.0',
                'text': keyword
            }

    def setTags(self, value):
        """ Setter
        """
        discovery_data = self.preview

        if discovery_data:
            discovery_tags = discovery_data[0]
            discovery_info = discovery_data[1]
            doc = self.context

            # ZCatalog brain
            if getattr(doc, 'getObject', None):
                doc = doc.getObject()
            field = doc.getField(self.field)
            mutator = field.getMutator(doc)

            logger.info(discovery_info)

            mutator(discovery_tags)
            doc.reindexObject(idxs=['Subject'])

    tags = property(getTags, setTags)
