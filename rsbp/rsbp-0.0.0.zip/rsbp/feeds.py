from django.contrib.syndication.views import Feed
from .models import Post
from . import app_settings

class LatestPostsFeed(Feed):
    title = app_settings.RSBP_FEED_TITLE
    description = app_settings.RSBP_FEED_DESCRIPTION
    link = app_settings.RSBP_FEED_LINK

    def items(self):
        return Post.objects.filter(published=True)[:app_settings.RSBP_FEED_MAX_ITEMS]

    def item_title(self, item):
        return item.downcast.feed_title()

    def item_description(self, item):
        return item.downcast.feed_description()

    def item_link(self, item):
        return item.downcast.get_absolute_url()

    def item_categories(self, item):
        return [tag.text for tag in item.tags.all()]

    def item_pubdate(self, item):
        return item.created
