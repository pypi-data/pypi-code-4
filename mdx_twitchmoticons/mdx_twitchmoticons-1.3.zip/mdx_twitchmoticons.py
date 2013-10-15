#!/usr/bin/env python


'''
Twitch Emoticon Extension for Python-Markdown
=============================================

Allows markdown to parse emoticon codes used on Twitch.tv

Usage
-----

    ### Default settings

    >>> import markdown
    >>> text = """I'm going to go get WR for WindWaker HD Kappa"""
    >>> html = markdown.markdown(text, ["twitchmoticons"])
    >>> print(html)
    <p>I'm going to go get WR for WindWaker HD <img class="tw_emote" src="http://static-cdn.jtvnw.net/jtv_user_pictures/chansub-global-emoticon-ddc6e3a8732cb50f-25x28.png" /></p>

    ### Custom settings

    >>> import markdown
    >>> text = """I'm going to go get WR for WindWaker HD Kappa"""
    >>> html = markdown.markdown(text,
    ...     extensions = ["twitchmoticons"],
    ...     extension_configs = {"twitchmoticons": [
    ...         ("EMOTICONS", {"WindWaker": "WindWaker.jpg" }),
    ...         ("BASE_URL",  "http://static.example.com/"   )
    ...     ]}
    ... )
    >>> print(html)
    <p>I'm going to go get WR for <img class="tw_emote" src="http://static.example.com/WindWaker.jpg" /> HD Kappa</p>

Dependencies
------------

* [Markdown 2.0+](http://www.freewisdom.org/projects/python-markdown/)
'''


import markdown
import re
from markdown.inlinepatterns import Pattern
from markdown.util import etree


class EmoticonPattern(Pattern):
    def __init__(self, pattern, emoticons):
        Pattern.__init__(self, pattern)
        self.emoticons = emoticons

    def handleMatch(self, m):
        emote = m.group("emote")
        img = etree.Element("img")
        img_location = "%s%s" % (
            self.emoticons.getConfig("BASE_URL"),
            self.emoticons.getConfig("EMOTICONS")[emote]
        )
        img.set("src", img_location)
        img.set("class", "tw_emote")
        return img


class TwitchmoticonExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            "EMOTICONS": [
                {
                    "Kappa"     : "chansub-global-emoticon-ddc6e3a8732cb50f-25x28.png",
                    "Keepo"     : "chansub-global-emoticon-8eed21805f6217ce-27x29.png",
                    "FrankerZ"  : "chansub-global-emoticon-3b96527b46b1c941-40x30.png",
                    "RalpherZ"  : "chansub-global-emoticon-3d9b59b17687288c-33x30.png",
                    "WinWaker"  : "chansub-global-emoticon-d4e971f7a6830e95-30x30.png",
                    "SSSsss"    : "chansub-global-emoticon-5d019b356bd38360-24x24.png",
                    "BibleThump": "chansub-global-emoticon-f6c13c7fc0a5c93d-36x30.png",
                    ":)"        : "chansub-global-emoticon-ebf60cd72f7aa600-24x18.png",
                    ";)"        : "chansub-global-emoticon-cfaf6eac72fe4de6-24x18.png",
                    ":D"        : "chansub-global-emoticon-9f2ac5d4b53913d7-24x18.png"
                },
                "A mapping of emoticon codes to image names."
            ],
            "BASE_URL": [
                "http://static-cdn.jtvnw.net/jtv_user_pictures/"
            ],
        }

        for key,value in configs.iteritems():
            self.config[key][0] = value

    def extendMarkdown(self, md, md_globals):
        self.md = md
        EMOTE_RE = r"(?<![^^/ ])(?P<emote>%s)" % "|".join(
            [re.escape(face) for face in self.getConfig("EMOTICONS").keys()]
        )
        md.inlinePatterns.add("emoticons", EmoticonPattern(EMOTE_RE, self), "<not_strong")


def makeExtension(configs={}):
    return TwitchmoticonExtension(configs=dict(configs))


if __name__ == "__main__":
    import doctest
    doctest.testmod()