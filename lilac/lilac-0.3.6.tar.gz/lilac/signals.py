# coding=utf8

"""All blinker signals in building process, actually this
enable as to make our plugins. And lilac use it in build-in
building process"""

# Thanks to blinker, great job!!

from blinker import signal

initialized = signal('initialized')
posts_parsed = signal('posts_parsed')
tags_extracted = signal('tags_extracted')
page_composed = signal('page_composed')
