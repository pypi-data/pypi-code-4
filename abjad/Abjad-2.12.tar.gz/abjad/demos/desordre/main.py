#! /usr/bin/env python

if __name__ == '__main__':

    from abjad import *
    from abjad.demos import desordre

    lilypond_file = desordre.make_desordre_lilypond_file()
    show(lilypond_file)
