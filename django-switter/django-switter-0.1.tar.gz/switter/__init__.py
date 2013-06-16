__version__ = '0.1'
__author__ = 'Sylwester Gruszka'

QUERY_TYPE_USER_TIMELINE = 'user_timeline'
QUERY_TYPE_SEARCH = 'search'

QUERY_TYPES_CHOICES = (
    (QUERY_TYPE_USER_TIMELINE, 'Tweets from user'),
    (QUERY_TYPE_SEARCH, 'Twitter search query'),
)

QUERY_TYPES = map(lambda x: x[0], QUERY_TYPES_CHOICES)
