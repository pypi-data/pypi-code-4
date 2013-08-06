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

import textteaser


if __name__ == '__main__':

    # replace 'foobarbaz' with your API key
    tt = textteaser.TextTeaser('foobarbaz')

    text = """
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
    title = 'Lorem ipsum example'

    sentences = tt.summarize(text, title)
    _id = tt._id

    # different text and title, but the same id
    cached_sentences = tt.summarize('Foo text', 'Foo title',
                                    kwargs={'id': _id})
    """
    The differing text and title values are ignored, and the id causes the
    previous result to be returned.

    sentences and cached sentences are the same list: [
        u'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        u'Sed sit amet ipsum mauris.',
        u'Nam tincidunt congue enim, ut porta lorem\nlacinia consectetur.',
        u'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        u'Aenean ut gravida\nlorem.'
    ]
    """
