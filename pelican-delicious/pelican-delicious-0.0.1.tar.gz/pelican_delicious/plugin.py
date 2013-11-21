# -*- coding: utf-8 -*-
"""
 for Pelican
=================================

This plugin allows you to embed `Delicious`_ bookmarks into your posts.

.. Delicious: https://delicious.com/

"""
import logging
import os
import re
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

delicious_regex = re.compile(r'\[delicious ([\s0-9a-zA-Z]+)\]')

delicious_template = """<div class="delicious">
{% for bookmark in bookmarks %}
    <dl>
        <dt>Title</dt>
        <dd>{{ bookmark.title }}</dd>
        {% if bookmark.description %}
        <dt>Description</dt>
        <dd>{{ bookmark.description }}</dd>
        {% endif %}
        <dt>URL</dt>
        <dd><a href="{{ bookmark.href }}">{{ bookmark.href }}</a></dd>
    </dl>
{% endfor %}
</div>"""


class Bookmark(object):

    def __init__(self, post):
        try:
            self.title = post['description']
        except KeyError:
            self.title = None

        try:
            self.description = post['extended']
        except KeyError:
            self.description = None

        try:
            self.href = post['href']
        except KeyError:
            self.href = None

        try:
            self.tags = set(post['tag'].split())
        except KeyError:
            self.tags = set()

delicious_bookmarks = None


def fetch_delicious(delicious_username, delicious_password):
    """Fetch bookmarks and return a list of bookmarks"""
    r = requests.get('https://api.delicious.com/v1/posts/all?&results=100000',
                     auth=(delicious_username, delicious_password))

    body = BeautifulSoup(r.content)
    return [Bookmark(p) for p in body.posts]


def setup_delicious(pelican):
    """Setup the default settings."""

    delicious_username = pelican.settings.get('DELICIOUS_USERNAME')
    delicious_password = pelican.settings.get('DELICIOUS_PASSWORD')
    pelican.settings['DELICIOUS_BOOKMARKS'] = fetch_delicious(
        delicious_username, delicious_password)


def replace_delicious_tags(generator):
    """Replace delicious tags in the article content."""
    from jinja2 import Template
    template = Template(delicious_template)

    for page in generator.pages:
        for match in delicious_regex.findall(page._content):
            bookmarks = [bookmark for bookmark
                         in generator.context.get('DELICIOUS_BOOKMARKS')
                         if set(match.split()).issubset(bookmark.tags)]

            # Create a context to render with
            context = generator.context.copy()
            context.update({'bookmarks': bookmarks})

            replacement = template.render(context)

            page._content = page._content.replace(match[0], replacement)


def register():
    """Plugin registration."""
    from pelican import signals

    signals.initialized.connect(setup_delicious)
    signals.page_generator_finalized.connect(replace_delicious_tags)
