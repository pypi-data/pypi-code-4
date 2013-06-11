# -*- coding: utf-8 -*-
import string
import urllib2
import json
import feedparser
import lxml.html as html

from cubicweb.server.sources import datafeed


class RSSParser(datafeed.DataFeedXMLParser):
    """datafeed parser for the rss feeds"""
    __regid__ = 'rss-parser'

    def process(self, url, raise_on_error=False, partialcommit=True):
        # Get source
        source = self._cw.execute('Any X WHERE X is CWSource, X type "datafeed", '
                                  'X parser "rss-parser", X url %(url)s',
                                  {'url': url}).get_entity(0,0)
        # Get uri for all rss to avoid multiple creation
        set_uris = set([u[0] for u in self._cw.execute('Any U WHERE X is NewsArticle, X uri U')])
        set_titles = set([t[0] for t in self._cw.execute('Any T WHERE X is NewsArticle, X title T')])
        try:
            data = feedparser.parse(url)
        except:
            return
        for entry in data.entries:
            try:
                feed = self.process_feed(entry)
                # Create entity
                if (feed['content'] and feed['title']
                    and feed['uri'] not in set_uris
                    and feed['title'] not in set_titles):
                    set_uris.add(feed['uri'])
                    set_titles.add(feed['title'])
                    entity = self._cw.create_entity('NewsArticle',
                                                    uri=feed['uri'],
                                                    title=feed['title'],
                                                    content=feed['content'],
                                                    source=source.eid)
            except:
                continue
        self._cw.commit()
        self._cw.set_cnxset()

    def process_feed(self, entry):
        item = {}
        item['uri'] = unicode(entry.get('id') or entry.get('link'))
        item['title'] = unicode(html.fromstring(entry.get('title', '')).text_content().strip())
        content = entry.get('content') or entry.get('summary_detail', '')
        if content:
            content = content.get('value', '')
        item['content'] = unicode(html.fromstring(content).text_content().strip())
        item['date'] = entry.get('updated')
        return item

