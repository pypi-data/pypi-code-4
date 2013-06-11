# -*- coding: utf-8 -*-
import string
import urllib2
import json
import feedparser
import lxml.html as html

from cubicweb.server.sources import datafeed


class TweetParser(datafeed.DataFeedXMLParser):
    """datafeed parser for the tweet feeds"""
    __regid__ = 'tweet-parser'
    NB_TWEETS = 50

    def process(self, url, raise_on_error=False, partialcommit=True):
        # Get source
        source = self._cw.execute('Any X WHERE X is CWSource, X type "datafeed", '
                                  'X parser "tweet-parser", X url %(url)s',
                                  {'url': url}).get_entity(0,0)
        # Get uri for all rss to avoid multiple creation
        set_ids = set([u[0] for u in self._cw.execute('Any U WHERE X is Tweet, X id_str U')])
        hashtags = dict([r for r in self._cw.execute('Any L, U WHERE U is HashTag, U label L')])
        baseurl = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=%s&count=%s&include_rts=true"
        data = urllib2.urlopen(baseurl % (url, self.NB_TWEETS))
        content = data.read()
        if not content:
            return
        for entry in json.loads(content):
            try:
                tweet = self.process_tweet(entry)
                # Create entity
                if tweet['title'] and not tweet['id'] in set_ids:
                    set_ids.add(tweet['id'])
                    entity = self._cw.create_entity('Tweet',
                                                    title=tweet['title'],
                                                    geo=tweet['geo'],
                                                    id_str=tweet['id'],
                                                    retweet=tweet['retweet'],
                                                    retweeted=tweet['retweeted'],
                                                    source=source.eid)
                    for tag in tweet['hashtags']:
                        if tag not in hashtags:
                            tag_entity = self._cw.create_entity('HashTag', label=unicode(tag))
                            hashtags[tag] = tag_entity.eid
                        self._cw.add_relation(entity.eid, 'has_hashtags', hashtags[tag])
            except:
                continue
        self._cw.commit()
        self._cw.set_cnxset()

    def process_tweet(self, entry):
        item = {}
        item['id'] = entry.get('id_str')
        item['title'] = unicode(entry.get('text', u''))
        item['geo'] = unicode(entry.get('geo', u''))
        item['retweet'] = int(entry.get('retweet_count')) if entry.get('retweet_count') else None
        item['retweeted'] = entry.get('retweeted', False)
        item['hashtags'] = set()
        if item['title']:
            for chunk in item['title'].split():
                chunk = chunk.strip()
                if chunk.startswith('#'):
                    chunk = chunk[1:].strip()
                    if not chunk:
                        continue
                    if chunk[-1] in string.punctuation:
                        chunk = chunk[:-1].strip()
                    if chunk:
                        item['hashtags'].add(chunk)
        return item
