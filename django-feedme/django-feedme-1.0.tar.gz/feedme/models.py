import datetime

from time import mktime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from hadrian.utils.slugs import unique_slugify

import feedparser

from .managers import FeedItemManager


class Category(models.Model):
    name = models.CharField(max_length=250, blank=True)
    slug = models.SlugField(blank=True, null=True, editable=False)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(Category, self).save(*args, **kwargs)

    @property
    def get_unread_count(self):
        return FeedItem.objects.my_feed_items(self.user).category(self.slug).un_read().count()


class Feed(models.Model):
    link = models.CharField(blank=True, max_length=450)
    url = models.CharField(blank=True, max_length=450)
    title = models.CharField(blank=True, null=True, max_length=250)
    category = models.ForeignKey(Category, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    last_update = models.DateField(blank=True, null=True, editable=False)

    class Meta:
        unique_together = (
            ("url", "user"),
        )

    def __unicode__(self):
        return self.url

    def _get_title(self):
        parser = feedparser.parse(self.url)
        return parser.feed.title

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self._get_title()
        super(Feed, self).save(*args, **kwargs)
        if self.last_update is None:
            self.update(force=True)

    @property
    def get_unread_count(self):
        return FeedItem.objects.filter(feed=self).un_read().count()

    def _update_feed(self):
        """ Perform a feed update.
        """
        # Update the last update field
        feed = feedparser.parse(self.url)
        self.last_update = datetime.date.today()
        if feed.feed.has_key("link"):
            self.link = feed.feed.link
        else:
            self.link = ""
        self.save()
        for item in feed.entries[:10]:
            # The RSS spec doesn't require the guid field so fall back on link
            if item.has_key("id"):
                guid = item.id
            else:
                guid = item.link

            # Search for an existing item
            try:
                FeedItem.objects.get(guid=guid)
            except FeedItem.DoesNotExist:
                # Create it.
                if item.has_key("published_parsed"):
                    pub_date = datetime.datetime.fromtimestamp(mktime(item.published_parsed))
                elif item.has_key("updated_parsed"):
                    pub_date = datetime.datetime.fromtimestamp(mktime(item.updated_parsed))
                else:
                    pub_date = datetime.datetime.now()

                feed_item = FeedItem(title=item.title, link=item.link, content=item.description,
                                     guid=guid, pub_date=pub_date, feed=self)
                feed_item.save()

    def _update_processor(self):
        if getattr(settings, 'FEED_UPDATE_CELERY', False):
            from .tasks import update_feed
            update_feed.delay(self)
            return True
        self._update_feed()
        return True

    def update(self, force=False):
        """ If we aren't forcing it
        and its not the same day, go ahead
        and update the feeds.
        """

        if force or not force and self.last_update < datetime.date.today():
            self._update_processor()
            return True

    @models.permalink
    def get_absolute_url(self):
        return ('feedme-feed-list-by-feed', (), {'feed_id': self.id})


class FeedItem(models.Model):
    title = models.CharField(max_length=350, blank=True)
    link = models.URLField(blank=True)
    content = models.TextField(blank=True)
    feed = models.ForeignKey(Feed, blank=True, null=True)
    read = models.BooleanField()
    guid = models.CharField(max_length=255)
    pub_date = models.DateTimeField()

    objects = FeedItemManager()

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.title

    def mark_as_read(self):
        """ Mark an item as read.
        """
        self.read = True
        self.save()

