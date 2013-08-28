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

    """
    sentences is a list: [
        u'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        u'Sed sit amet ipsum mauris.',
        u'Nam tincidunt congue enim, ut porta lorem\nlacinia consectetur.',
        u'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        u'Aenean ut gravida\nlorem.'
    ]
    """

    # alternately, you can summarize an article from a URL

    url = 'https://en.wikipedia.org/wiki/Alan_turing'
    sentences = tt.summarize(url=url)

    """
    sentences is a list: [
        u'He went on to prove that there was no solution to the
          Entscheidungsproblem by first showing that the halting problem for
          Turing machines is undecidable: in general, it is not possible to
          decide algorithmically whether a given Turing machine will ever
          halt.',
        u"It was also novel in its notion of a 'Universal Machine' (now known
          as a Universal Turing machine), with the idea that such a machine
          could perform the tasks of any other machine, or in other words, it
          is provably capable of computing anything that is computable.",
        u'30 In June 1938, he obtained his PhD from Princeton; 31 his
          dissertation, Systems of Logic Based on Ordinals, 32 33 introduced
          the concept of ordinal logic and the notion of relative computing,
          where Turing machines are augmented with so-called oracles, allowing
          a study of problems that cannot be solved by a Turing machine.',
        u'115\n\nIn 1999, Time Magazine named Turing as one of the 100 Most
          Important People of the 20th century and stated: "The fact remains
          that everyone who taps at a keyboard, opening a spreadsheet or a
          word-processing program, is working on an incarnation of a Turing
          machine." 3 Turing is featured in the 1999 Neal Stephenson novel
          Cryptonomicon.',
        u'On 23 June 2012, Google featured an interactive doodle where
          visitors had to change the instructions of a Turing Machine, so when
          run, the symbols on the tape would match a provided sequence,
          featuring "Google" in Baudot-Murray code.'
    ]
    """
