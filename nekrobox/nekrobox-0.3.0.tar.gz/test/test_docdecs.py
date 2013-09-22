#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_docdecs
------------

Tests for `nekrobox.docdecs` module.
"""
from nekrobox import docdecs


class TestNekrobox(object):
    def test_params(self):
        @docdecs.params(word=(str, 'echo this word'))
        def echo(word):
            return word
        assert echo.__doc__ == ":param str word: echo this word"

    def test_params_with_return_type_doc(self):
        @docdecs.params(text=(str, 'text to make lowercase'),
                        returns=(str, 'lowercase version of text'))
        def lowercase(text):
            return text.lower()
        assert lowercase.__doc__ == """:param str text: text to make lowercase
:return: lowercase version of text
:rtype: str"""
