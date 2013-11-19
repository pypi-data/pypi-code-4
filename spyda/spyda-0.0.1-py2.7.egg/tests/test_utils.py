from keyword import kwlist

import pytest

from spyda.utils import dict_to_text, get_close_matches, unichar_to_text, unescape, UNICHAR_REPLACEMENTS


TEST_ENTITIES = (
    ("&nbsp;",  u"\xa0"),
    ("&lsquo;", u"\u2018"),
    ("&rsquo;", u"\u2019"),
    ("&ldquo;", u"\u201c"),
    ("&rdquo;", u"\u201d"),
)


TEST_UNICHARS = UNICHAR_REPLACEMENTS


def pytest_generate_tests(metafunc):
    if "entity" in metafunc.fixturenames:
        metafunc.parametrize(["entity", "expected"], TEST_ENTITIES)
    elif "unichar" in metafunc.fixturenames:
        metafunc.parametrize(["unichar", "expected"], TEST_UNICHARS)


def test_dict_to_text():
    d = {"foo": "bar"}
    s = "foo: bar"
    assert dict_to_text(d) == s


@pytest.mark.parametrize(("input", "expected"), [
    (("appel", ["ape", "apple", "peach", "puppy"]), [("apple", 0.8), ("ape", 0.75)]),
    (("wheel", kwlist), [("while", 0.6)]),
    (("apple", kwlist), []),
    (("accept", kwlist), [("except", 0.6666666666666666)])
])
def test_get_close_matches(input, expected):
    assert get_close_matches(*input) == expected

def test_unescape(entity, expected):
    actual = unescape(entity)
    assert actual == expected


def test_unescape_hex():
    entity = "&#xa0;"
    assert unescape(entity) == u"\xa0"


def test_unescape_invalid_hex():
    entity = "&#xzz;"
    assert unescape(entity) == entity


def test_unescape_int():
    entity = "&#160;"
    assert unescape(entity) == u"\xa0"


def test_unescape_invalid():
    entity = "&foobar;"
    assert unescape(entity) == entity


def test_unichar_to_text(unichar, expected):
    actual = unichar_to_text(unichar)
    assert actual == expected
