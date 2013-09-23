from django.contrib.syndication.views import Feed
from django.utils import feedgenerator

from wheelcms_axle.actions import action_registry
from wheelcms_axle.content import Content


class WheelFeed(Feed):
    """ Can we somehow (optionally) include the entire body? """
    def __init__(self, spoke):
        super(WheelFeed, self).__init__()
        self.spoke = spoke

    def link(self):
        return self.spoke.path() + '/+' + self.action

    def title(self):
        return "Feed for %s" % self.spoke.instance.title

    def description(self):
        return self.spoke.instance.description

    def items(self):
        if hasattr(self.spoke, 'feed'):
            return self.spoke.feed()

        ## XXX Use Content object manager, once available
        instance = self.spoke.instance

        return Content.objects.filter(node__tree_path__startswith=instance.node.tree_path, language=instance.language, state="published").order_by("-created")

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    @classmethod
    def handler(cls, handler, request, action):
        return cls(handler.spoke())(request)

class AtomWheelFeed(WheelFeed):
    action = "atom"

    feed_type = feedgenerator.Atom1Feed

class RSS1WheelFeed(WheelFeed):
    action = "rss091"

    feed_type = feedgenerator.RssUserland091Feed

class RSS2WheelFeed(WheelFeed):
    action = "rss2"

    feed_type = feedgenerator.Rss201rev2Feed

class DefaultWheelFeed(RSS2WheelFeed):
    action = "rss"


action_registry.register(RSS1WheelFeed.handler, RSS1WheelFeed.action)
action_registry.register(RSS2WheelFeed.handler, RSS2WheelFeed.action)
action_registry.register(DefaultWheelFeed.handler, DefaultWheelFeed.action)
action_registry.register(AtomWheelFeed.handler, AtomWheelFeed.action)

