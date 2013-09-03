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

import logging
import textteaser

"""A simple example of how to use logging.

For more information about logging in Python,
see: http://docs.python.org/library/logging.html

"""


if __name__ == '__main__':

    # get the texteaser logger
    logger = logging.getLogger('textteaser')

    # set the logging level
    logger.setLevel(logging.DEBUG)

    # create a log formatter
    formatter = logging.Formatter('%(name)s-%(levelname)s: %(message)s')

    # create a log handler
    handler = logging.StreamHandler()

    # apply the formatter to the handler
    handler.setFormatter(formatter)

    # add the handler
    logger.addHandler(handler)

    # replace 'foobarbaz' with your API key
    tt = textteaser.TextTeaser('foobarbaz')
    tt.summarize(url='https://en.wikipedia.org/wiki/Alan_turing')

    """The following will be logged:

        textteaser.textteaser.TextTeaser-DEBUG: posting to url:
        https://textteaser.p.mashape.com/api with data: {
            'url': 'https://en.wikipedia.org/wiki/Alan_turing',
            'text': None,
            'title': None
        }
        textteaser.textteaser.TextTeaser-DEBUG: received response: {
            u'title': u'Wikipedia, the free encyclopedia',
            u'summaryId': u'3wbgVQ',
            u'sentences': [
                u'He went on to prove that there was no solution to the]
                    Entscheidungsproblem by first showing that the halting
                    problem for Turing machines is undecidable: in general,
                    it is not possible to decide algorithmically whether a
                    given Turing machine will ever halt.',
                u"It was also novel in its notion of a 'Universal Machine' (now
                    known as a Universal Turing machine), with the idea that
                    such a machine could perform the tasks of any other
                    machine, or in other words, it is provably capable of
                    computing anything that is computable.",
                u'30 In June 1938, he obtained his PhD from Princeton; 31 his
                    dissertation, Systems of Logic Based on Ordinals, 32 33
                    introduced the concept of ordinal logic and the notion of
                    relative computing, where Turing machines are augmented
                    with so-called oracles, allowing a study of problems that
                    cannot be solved by a Turing machine.',
                u'115\n\nIn 1999, Time Magazine named Turing as one of the 100
                    Most Important People of the 20th century and stated: "The
                    fact remains that everyone who taps at a keyboard, opening
                    a spreadsheet or a word-processing program, is working on
                    an incarnation of a Turing machine." 3 Turing is featured
                    in the 1999 Neal Stephenson novel Cryptonomicon.',
                u'On 23 June 2012, Google featured an interactive doodle where
                    visitors had to change the instructions of a Turing
                    Machine, so when run, the symbols on the tape would match
                    a provided sequence, featuring "Google" in Baudot-Murray
                    code.'
            ]
        }

    """
