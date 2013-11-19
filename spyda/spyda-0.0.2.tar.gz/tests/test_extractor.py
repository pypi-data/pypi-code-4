#!/usr/bin/env python

import pytest

from os import path

from spyda.extractor import extract

from .helpers import urljoin


@pytest.fixture()
def sample_file(request):
    root = path.dirname(__file__)
    return path.relpath(path.join(root, "docroot", "sample.html"), path.join(path.dirname(__file__), ".."))


@pytest.fixture()
def sample_url(request, webapp):
    return urljoin(webapp.server.base, "sample.html")


@pytest.fixture()
def sample_url_index(request, webapp):
    return urljoin(webapp.server.base, "sample/")


@pytest.fixture()
def filters(request):
    return ["title=#article .title", "content=#article #content", "img.src=img"]


@pytest.fixture()
def expected_result(request):
    return {
        "title": ["Test Article"],
        "_title": ["<p class=\"title\">Test Article</p>\n"],
        "content": ["James Mills says \"Hello World!\""],
        "_content": ["""<div id="content">\n<p>James Mills says "Hello World!"</p>\n<img alt="Test Img1" src="http://www.testsite.com/img1.jpg">\n<img alt="Test Img2" src="http://www.testsite.com/img2.jpg">\n</div>\n"""],
        "img": ["http://www.testsite.com/img1.jpg", "http://www.testsite.com/img2.jpg"],
        "_img": ["http://www.testsite.com/img1.jpg", "http://www.testsite.com/img2.jpg"],
    }


def test_extract_file(sample_file, filters, expected_result):
    result = extract(sample_file, filters)
    assert result == expected_result


def test_extract_file_null(sample_file):
    filters = ("foo=bar",)
    expected_result = {"foo": [], "_foo": []}

    result = extract(sample_file, filters)
    assert result == expected_result


def test_extract_url(sample_url, filters, expected_result):
    result = extract(sample_url, filters)
    assert result == expected_result
