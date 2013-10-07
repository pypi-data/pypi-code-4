""" Utility for related items
"""
from bs4 import BeautifulSoup
from zope.interface import implements
from eea.alchemy.interfaces import IDiscoverLinks

class DiscoverLinks(object):
    """ Discover internal links
    """
    implements(IDiscoverLinks)

    def __call__(self, text="", match=""):
        match = match.replace('https://', 'http://')
        soup = BeautifulSoup(text)

        items = []
        for link in soup.find_all('a'):
            href = link.get('href')
            href = href.replace('https://', 'http://')

            if u'resolveuid' in href:
                if href not in items:
                    items.append(href)
            elif match and href.startswith(match):
                found = href[len(match):]
                found = found.strip('/')
                if found not in items:
                    items.append(found)
            elif href.startswith('/'):
                href = href.strip('/')
                if href not in items:
                    items.append(href)

        for link in items:
            yield {
                'count': 1,
                'type': 'Link',
                'text': link,
                'relevance': '100.0'
            }
