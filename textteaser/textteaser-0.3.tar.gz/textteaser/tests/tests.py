#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Jeffrey Goettsch and other contributors.
#
# This file is part of py-textteaser.
#
# py-textteaser is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# py-textteaser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with py-textteaser.  If not, see
# <http://www.gnu.org/licenses/>.


import unittest

import textteaser

from . import apikey


class TextTeaserTest(unittest.TestCase):

    def setUp(self):

        self.tt = textteaser.TextTeaser(apikey.APIKEY)
        self.text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus.
Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nek
consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero
egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem
lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor.
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida
lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor.
Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim
sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in
urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam
pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis
parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris
vitae nisi at sem facilisis semper ac in est.


Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae,
sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare,
ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem
nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat,
non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum
et, tincidunt et orci. Fusce eget orci a orci congue vestibulum. Ut dolor diam,
elementum et vestibulum eu, porttitor vel elit. Curabitur venenatis pulvinar
tellus gravida ornare. Sed et erat faucibus nunc euismod ultricies ut id justo.
Nullam cursus suscipit nisi, et ultrices justo sodales nec. Fusce venenatis
facilisis lectus ac semper. Aliquam at massa ipsum. Quisque bibendum purus
convallis nulla ultrices ultricies. Nullam aliquam, mi eu aliquam tincidunt,
purus velit laoreet tortor, viverra pretium nisi quam vitae mi. Fusce vel
volutpat elit. Nam sagittis nisi dui.
        """

    def test_summarize_text(self):
        """Test the normal operation of the summarize method with text
        and a title.

        """

        title = 'Lorem ipsum'
        sentences = self.tt.summarize(self.text, title)

        self.assertEqual(200, self.tt.status_code)
        self.assertEqual(self.tt.title, title)
        self.assertIsNotNone(self.tt.sentences)
        self.assertEqual(self.tt.sentences, sentences)

    def test_summarize_url(self):
        """Test the normal operation of the summarize method with a url.

        """

        url = 'http://en.wikipedia.org/wiki/Alan_turing'
        self.tt.summarize(url=url)

        self.assertEqual(200, self.tt.status_code)
        self.assertIsNotNone(self.tt.sentences)

    def test_summarize_kwargs(self):
        """Test the summarize method with kwargs.

        """

        title = 'Lorem ipsum'
        kwargs = {
            'category': 'Category Foo',
            'blog': 'Blog Foo',
        }
        sentences = self.tt.summarize(self.text, title, kwargs=kwargs)

        self.assertEqual(200, self.tt.status_code)
        self.assertEqual(self.tt.title, title)
        self.assertIsNotNone(self.tt.sentences)
        self.assertEqual(self.tt.sentences, sentences)

    def test_summarize_apikey_invalid(self):
        """An invalid API key should raise an APIKeyError.

        """

        title = 'bad API key'
        self.tt.apikey = 'foo'
        self.assertRaises(textteaser.exceptions.APIKeyError, self.tt.summarize,
                          self.text, title)

    def test_summarize_long_text(self):
        """Too large of a text parameter should raise a ServerError.

        """

        title = 'Long lorem ipsum'
        self.assertRaises(textteaser.exceptions.ServerError, self.tt.summarize,
                          self.text*200, title)
