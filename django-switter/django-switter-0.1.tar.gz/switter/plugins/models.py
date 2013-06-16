from datetime import datetime, timedelta
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from annoying.functions import get_object_or_None
from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils import simplejson as json

from switter import QUERY_TYPES_CHOICES, QUERY_TYPE_SEARCH, QUERY_TYPE_USER_TIMELINE
from switter.models import CachedTweets
from switter.plugins.settings import TWEETS_TEMPLATES
from switter.settings import CACHE_TIME


class SwitterTweets(CMSPlugin):
    COUNT_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    header = models.CharField(max_length=255, default='Latest Tweets', blank=True)
    query_type = models.CharField(max_length=255, choices=QUERY_TYPES_CHOICES,
                                  default=QUERY_TYPE_USER_TIMELINE)
    twitter_id = models.CharField(max_length=255, default='', blank=True,
                                  verbose_name="Twitter username")
    search_query = models.CharField(max_length=255, default='', blank=True,
                                    verbose_name="Twitter search query")
    show_retweets = models.BooleanField(default=True)
    show_replies = models.BooleanField(default=True)
    count = models.IntegerField(choices=COUNT_CHOICES, default=3,
                                verbose_name="Max. number of tweets")
    render_template = models.CharField(max_length=255, choices=TWEETS_TEMPLATES,
                                       default=TWEETS_TEMPLATES[0][0], verbose_name="Template")
    def __unicode__(self):
        if self.search_query:
            return "Tweets: %s" % self.search_query
        return "Tweets by %s" % self.twitter_id

    def save(self, *args, **kwargs):
        if self.twitter_id.startswith("@"):
            self.twitter_id = self.twitter_id[1:]
        super(SwitterTweets, self).save(*args, **kwargs)

    def get_jquery_ajax_data(self):
        """
        A convenience method, used to get json data for jquery ajax calls
        straight away in the templates.
        """
        data = OrderedDict()

        if self.query_type == 'user_timeline':
            data['screen_name'] = self.twitter_id
        else:
            data['q'] = self.search_query

        data['count'] = self.count
        data['exclude_replies'] = not self.show_replies
        data['include_rts'] = self.show_retweets
        return json.dumps(data)

    def get_tweets_json(self):
        """
        Returns JSON version of tweets fetched (or not) from get_tweets().
        For convenient use in templates.
        """
        js = json.dumps(self.get_tweets())
        return js

    def get_tweets(self):
        """
        Returns tweets (python obj) or None if there's nothing cached.
        We don't fetch tweets if there's no fresh cached ones,
        javascript will do it in order not to increase page load time.
        """
        min_age = datetime.now() - timedelta(seconds=CACHE_TIME)
        if self.query_type == QUERY_TYPE_USER_TIMELINE:
            cached_tweets = get_object_or_None(CachedTweets,
                                               query_type=self.query_type,
                                               query_value="screen_name=%s&count=%s" % \
                                                           (self.twitter_id, self.count),
                                               modified__gte=min_age)
        elif self.search_query == QUERY_TYPE_SEARCH:
            cached_tweets = get_object_or_None(CachedTweets,
                                               query_type=self.query_type,
                                               query_value="q=%s&count=%s" % \
                                                           (self.search_query, self.count),
                                               modified__gte=min_age)

        if cached_tweets:
            return cached_tweets.cached_response
