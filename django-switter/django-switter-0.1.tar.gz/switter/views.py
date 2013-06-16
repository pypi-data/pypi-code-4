from datetime import datetime, timedelta

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.utils import simplejson as json
from django.utils.http import urlunquote

from switter import QUERY_TYPES
from switter.models import CachedTweets
from switter.settings import CACHE_TIME


class SwitterTweetsView(View):
    """
    An AJAX view for fetching tweets. Returns JSON list of tweets.
    """

    def get(self, *args, **kwargs):
        q_type = self.kwargs['query_type']
        q = urlunquote(self.request.META['QUERY_STRING'])

        if q_type not in QUERY_TYPES:
            # Bad request, return error message
            valid_choices = ", ".join(QUERY_TYPES)
            content = {"error": "Invalid query type. Valid types are: %s." % valid_choices}
            return HttpResponseBadRequest(
                json.dumps(content),
                content_type="application/json"
            )

        cached_tweets, created = CachedTweets.objects.get_or_create(
                                    query_type=q_type,
                                    query_value=q
                                )

        # fetch new tweets from twitter only if cached ones are too old
        min_age = datetime.now() - timedelta(seconds=CACHE_TIME)
        if created or cached_tweets.modified < min_age:
            cached_tweets.update_tweets()

        return HttpResponse(
            json.dumps(cached_tweets.cached_response),
            content_type="application/json"
        )
