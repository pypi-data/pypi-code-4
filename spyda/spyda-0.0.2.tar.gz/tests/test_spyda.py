#!/usr/bin/env python

import pytest

from spyda.utils import fetch_url, get_links


from .helpers import urljoin

SAMPLE_CONTENT = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

<head>
 <title>/</title>
</head>

<body>
 <p>Hello World!</p>
 <p><a href=".">.</a></p>
 <p><a href="..">..</a></p>
 <p><a href="foo/">foo/</a></p>
 <p>
  Test suite created by
  <a href="mailto:foo@bar.com">
   Foo Bar, foo at bar dot com
  </a>
 </p>
</body>
</html>
"""


SAMPLE_LINKS = [".", "..", "foo/", "mailto:foo@bar.com"]


@pytest.fixture()
def sample_content():
    return SAMPLE_CONTENT


@pytest.fixture()
def sample_links():
    return SAMPLE_LINKS


def test_fetch_url(webapp):
    res, data = fetch_url(urljoin(webapp.server.base, "hello"))
    assert res.status == 200
    assert data == b"Hello World!"


def test_fetch_url_unicode(webapp):
    res, data = fetch_url(urljoin(webapp.server.base, "unicode"))
    assert res.status == 200
    assert data == u"Hello World!"


def test_get_links(sample_content, sample_links):
    actual_links = list(get_links(sample_content))
    assert actual_links == sample_links
