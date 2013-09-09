#!/usr/

import html.parser as _html_parser
import sys as _sys


class HTMLReferenceReplacer (_html_parser.HTMLParser):
    def __init__(self, targets=None):
        if _sys.version_info < (3, 5):
            kwargs = {'strict': False}
        super(HTMLParser.__init__(self, **kwargs))
        if targets is None:
            targets = {}
        self.targets = targets

    def handle_starttag(self, tag, attrs):
        target_attrs = self.targets.get(tag, [])
        for i,(name,value) in enumerate(attrs):
            if name in target_attrs:
                attrs[i] = (name, ...)
