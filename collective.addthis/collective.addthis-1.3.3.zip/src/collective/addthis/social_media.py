# -*- coding: utf-8 -*-
import json
import urllib
import socket
from zope.interface import implements, alsoProvides
from zope import component
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from collective.addthis.interfaces import ISocialMedia
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry


SHARING = "http://cache.addthiscdn.com/services/v1/sharing.en.json"


class SocialMediaSources(object):
    """Provides a list of Social Media supported by the addthis.com service."""
    implements(ISocialMedia)

    def _services(self):
        """Returns the services using that addthis API"""
        registry = component.queryUtility(IRegistry)
        return registry.get('collective.addthis.socialmediasources', [])

    @property
    def sources(self):
        for service in self._services():
            token, title = service.split('|')
            yield (token.encode('ascii'), title,)
        raise StopIteration


def socialMediaVocabulary(context):
    """Vocabulary factory for social media sources."""
    utility = component.getUtility(ISocialMedia)
    terms = [SimpleTerm(token, token, title)
             for token, title in utility.sources]
    return SimpleVocabulary(terms)

alsoProvides(socialMediaVocabulary, IVocabularyFactory)


class SocialMediaUpdater(BrowserView):
    """Update the data used by the vocabulary"""

    def __call__(self):
        raw_services = self._services()

        if not raw_services:
            return u"no services retrieved, don't update the configuration"
        services = []

        for service in raw_services:
            value = '%s|%s' % (service['code'], service['name'])
            if not isinstance(value, unicode):
                try:
                    value = unicode(value, 'utf-8')
                except TypeError:
                    value = value.encode('ascii', 'ignore')
            services.append(value)

        registry = component.queryUtility(IRegistry)
        registry['collective.addthis.socialmediasources'] = tuple(services)
        return u"%s services retrieved" % len(services)

    def _services(self):
        """Returns the services using addthis API"""

        try:
            old_default = socket.getdefaulttimeout()
            socket.setdefaulttimeout(5)
            response = urllib.urlopen(SHARING)
            socket.setdefaulttimeout(old_default)
        except IOError:
            return []
        except socket.timeout:
            return []

        if response.code == 200:
            data = json.load(response)
            if data:
                return data[u'data']
        return []
