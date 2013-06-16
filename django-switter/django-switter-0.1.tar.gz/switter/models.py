from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_extensions.db.fields.json import JSONField

from switter import tweets, QUERY_TYPES_CHOICES, QUERY_TYPE_USER_TIMELINE


class CachedTweets(models.Model):
    """
    This is a model that will cache twitter's query results.
    """
    query_type = models.CharField(max_length=255, choices=QUERY_TYPES_CHOICES,
                                  default=QUERY_TYPE_USER_TIMELINE)
    query_value = models.CharField(max_length=255, default="", blank=True)

    cached_response = JSONField(default="", blank=True)

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    class Meta:
        unique_together = (('query_type', 'query_value'),)

    def update_tweets(self):
        self.cached_response = tweets.fetch_tweets(self.query_type, self.query_value)
        self.save()
