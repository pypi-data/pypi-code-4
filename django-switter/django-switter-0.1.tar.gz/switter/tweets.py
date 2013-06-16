from django.http import QueryDict
from twython import Twython

from switter import settings, QUERY_TYPES, QUERY_TYPE_USER_TIMELINE, QUERY_TYPE_SEARCH


def fetch_tweets(query_type, query_value):
    """
     Returns raw JSON from twitter.
    """

    if query_type not in QUERY_TYPES:
        return

    query_params = {}
    for key, val in QueryDict(query_value).items():
        query_params[key] = val

    t = Twython(
        settings.CONSUMER_KEY,
        settings.CONSUMER_SECRET,
        settings.ACCESS_TOKEN,
        settings.ACCESS_TOKEN_SECRET,
    )

    # TODO: check if we can access Twitter API with this credentials
    #       and shout if not! (or just raise warning and return none?)

    # TODO: use getattr to allow any valid twitter endpoint
    if query_type == QUERY_TYPE_USER_TIMELINE:
        return t.get_user_timeline(**query_params)

    elif query_type == QUERY_TYPE_SEARCH:
        return t.search(**query_params)

    return
