""" Auto-discover geotags API
"""
import logging
from zope.interface import implements
from zope.component import getUtility, queryAdapter
from zope.component.hooks import getSite
from eea.alchemy.interfaces import IDiscoverGeoTags
from eea.alchemy.interfaces import IDiscoverGeographicalCoverage
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
logger = logging.getLogger('eea.alchemy.discover')

class DiscoverGeoTags(object):
    """ Common adapter to auto-discover geotags in context metadata
    """
    implements(IDiscoverGeoTags)

    def __init__(self, context):
        self.context = context
        self._key = None
        self.field = 'location'
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
            logger.warn('%s has no %s schema field. location not set',
                        doc.absolute_url(1), self.field)
            return

        mutator = field.getMutator(doc)
        if not mutator:
            logger.warn("Can't edit field %s for doc %s",
                        self.field, doc.absolute_url(1))
            return

        current = field.getAccessor(doc)()
        if current and isinstance(current, (str, unicode)):
            # Location already set, skip as we don't want to mess it
            return

        tags = set(tag.get('text') for tag in self.tags)
        if current:
            if isinstance(current, (str, unicode)):
                tags.add(current)
            else:
                tags = tags.union(current)

        if not tags:
            return

        tags = list(tags)
        tags.sort()
        if isinstance(current, (str, unicode)):
            tags = ', '.join(tags)

        return (tags, 'Update %s for %s. \n Before: %s \n After: %s' %
                        (self.field, doc.absolute_url(1), current, tags))

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
        if not self.key:
            return

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

            string += '\n' + text

        discover = getUtility(IDiscoverGeographicalCoverage)
        if not discover:
            return

        string = string.strip()
        if not string:
            return

        for item in discover(self.key, string):
            yield item

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
            doc.reindexObject(idxs=['location'])

    tags = property(getTags, setTags)
