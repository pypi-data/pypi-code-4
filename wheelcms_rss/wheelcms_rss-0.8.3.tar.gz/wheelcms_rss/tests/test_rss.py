from wheelcms_axle.tests.models import Type1, Type1Type
from wheelcms_axle.node import Node
from wheelcms_rss.feeds import WheelFeed

class TestRSS(object):
    def test_simple(self, client):
        """ simple case """
        root = Node.root()
        content = Type1(title="Hello World", state="published", node=root).save()
        spoke = content.spoke()
        feed = WheelFeed(spoke)
        assert content.content_ptr in feed.items()

    def test_languages(self, client):
        """ restrict to the content's language """
        root = Node.root()
        en = Type1(title="Hello World", state="published",
                   node=root, language="en").save()
        nl = Type1(title="Hoi Wereld", state="published",
                   node=root, language="nl").save()
        enspoke = en.spoke()
        feed = WheelFeed(enspoke)
        assert en.content_ptr in feed.items()
        assert nl.content_ptr not in feed.items()

    def test_unpublished(self, client):
        """ only published content """
        root = Node.root()
        rootcontent = Type1(title="Root", state="published", node=root).save()
        pub_content = Type1(title="Published", state="published",
                            node=root.add("pub")).save()
        unpub_content = Type1(title="Private", state="private",
                              node=root.add("unpub")).save()
        spoke = rootcontent.spoke()
        feed = WheelFeed(spoke)
        assert pub_content.content_ptr in feed.items()
        assert unpub_content.content_ptr not in feed.items()
