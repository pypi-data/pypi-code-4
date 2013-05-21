""" EEA Alchemy public interfaces
"""
from zope.interface import Interface
from zope import schema

class IAlchemyAPI(Interface):
    """ Utility to use AlchemyAPI (http://alchemyapi.com) using zope.components

    >>> from zope.component import getUtility
    >>> from eea.alchemy.interfaces import IAlchemyAPI
    >>> util = getUtility(IAlchemyAPI)
    >>> util.setAPIKey('12345')

    >>> res = util.TextGetRankedNamedEntities(
    ...          'Formation of new land cover in the region of Valencia, Spain')

    >>> entities = res['entities']
    >>> [entity['text'] for entity in entities]
    ['Spain', 'Valencia']

    >>> [entity['type'] for entity in entities]
    ['Country', 'City']

    """

class IAlchemyDiscoverable(Interface):
    """ Marker interface for discoverable items
    """
#
# Utilities
#
class IDiscoverTemporalCoverage(Interface):
    """ Auto discover temportal coverage from text
    """
    def __call__(text=""):
        """ Return an iterable with discovered time periods:

        >>> from zope.component import getUtility
        >>> from eea.alchemy.interfaces import IDiscoverTemporalCoverage

        >>> discover = getUtility(IDiscoverTemporalCoverage)
        >>> res = discover('Publication 1990-2010 until 2010 -  2030')

        res
        [{
          'count': '1',
          'relevance': '100.0',
          'type': 'Time',
          'text': '1990-2010'
        }, ...]

        >>> res.next()['text']
        '1990-2010'

        >>> res.next()['text']
        '2010-2030'

        Keyword arguments:
        text -- string to look in for temporal coverage
        """

class IDiscoverGeographicalCoverage(Interface):
    """ Auto discover geographical coverage from text
    """
    def __call__(key, text=""):
        """ Return an iterable with discovered geotags

        >>> from zope.component import getUtility
        >>> from eea.alchemy.interfaces import IDiscoverGeographicalCoverage

        >>> discover = getUtility(IDiscoverGeographicalCoverage)
        >>> res = discover("12345",
        ...      'Formation of new land cover in the region of Valencia, Spain')

        res
        [{
          'count': '1',
          'relevance': '0.90',
          'type': 'Country',
          'text': 'Spain'
        }, ...]

        >>> res.next()['text']
        'Spain'

        >>> res.next()['text']
        'Valencia'


        Keyword arguments:
        key -- Alchemy API authentication key
        text -- string to look in for geotags
        """

class IDiscoverKeywords(Interface):
    """ Auto discover keywords from text
    """
    def __call__(key, text=""):
        """ Return an iterable with discovered keywords

        >>> from zope.component import getUtility
        >>> from eea.alchemy.interfaces import IDiscoverKeywords

        >>> discover = getUtility(IDiscoverKeywords)
        >>> res = discover("12345",
        ...      'Formation of new land cover in the region of Valencia, Spain')

        res
        [{
          'relevance': '0.99',
          'text': 'new land cover'
        }, ...]

        >>> res.next()['text']
        'new land cover'

        Keyword arguments:
        key -- Alchemy API authentication key
        text -- string to look in for geotags
        """


#
# Adapters
#
class IDiscoverGeoTags(Interface):
    """ Auto discover location from object metadata (title, description)

        metadata -- object metadata to look in for geotags
        tags -- get/set(persist to ZODB) discovered geotags

        >>> from zope.component import getAdapter
        >>> from eea.alchemy.interfaces import IDiscoverGeoTags
        >>> discover = getAdapter(self.sandbox, IDiscoverGeoTags)
        >>> discover.metadata = 'title'
        >>> [tag.get('text', '') for tag in discover.tags]
        ['Spain', 'Valencia']

        >>> [tag.get('type', '') for tag in discover.tags]
        ['Country', 'City']

        >>> discover.metadata = 'description'
        >>> [tag.get('text', '') for tag in discover.tags]
        ['Venice']

        >>> [tag.get('type', '') for tag in discover.tags]
        ['StateOrCounty']

        This adapter can also be applied on ZCatalog brains

        >>> discover = getAdapter(self.brain, IDiscoverGeoTags)
        >>> discover.metadata = 'Title'
        >>> [tag.get('text', '') for tag in discover.tags]
        ['Spain', 'Valencia']

    """
    metadata = schema.List(title=u'Metadata', value_type=schema.TextLine())
    tags = schema.Iterable(title=u'Tags')

class IDiscoverTags(Interface):
    """ Auto discover keywords from object metadata (title, description)

        metadata -- object metadata to look in for keywords
        tags -- get/set (persist to ZODB) discovered keywords

        >>> from zope.component import getAdapter
        >>> from eea.alchemy.interfaces import IDiscoverTags
        >>> discover = getAdapter(self.sandbox, IDiscoverTags)
        >>> discover.metadata = 'title'
        >>> [tag.get('text', '') for tag in discover.tags]
        [u'new land cover']

        This adapter can also be applied on ZCatalog brains

        >>> discover = getAdapter(self.brain, IDiscoverTags)
        >>> discover.metadata = 'Title'
        >>> [tag.get('text', '') for tag in discover.tags]
        [u'new land cover']

    """
    metadata = schema.List(title=u'Metadata', value_type=schema.TextLine())
    tags = schema.Iterable(title=u'Tags')

class IDiscoverTime(Interface):
    """ Auto discover time coverage from object metadata (title, description)

        metadata -- object metadata to look in for time periods
        tags -- get/set (persist to ZODB) discovered keywords

        >>> from zope.component import getAdapter
        >>> from eea.alchemy.interfaces import IDiscoverTime
        >>> discover = getAdapter(self.sandbox, IDiscoverTime)
        >>> discover.metadata = 'description'
        >>> [tag.get('text', '') for tag in discover.tags]
        ['1990-2000']

        This adapter can also be applied on ZCatalog brains

        >>> discover = getAdapter(self.brain, IDiscoverTime)
        >>> discover.metadata = 'Description'
        >>> [tag.get('text', '') for tag in discover.tags]
        ['1990-2000']

    """
    metadata = schema.List(title=u'Metadata', value_type=schema.TextLine())
    tags = schema.Iterable(title=u'Tags')
