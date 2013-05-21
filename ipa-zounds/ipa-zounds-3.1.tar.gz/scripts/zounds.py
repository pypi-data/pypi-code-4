#!/usr/bin/env python

# IPA Zounds, a sound change engine with support for the IPA.
# Copyright 2003 Jamie Norrish
#
# This file is part of IPA Zounds.
#
# IPA Zounds is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPA Zounds is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""This is the Zounds command-line program for IPA Zounds."""

import codecs
import gettext
from optparse import OptionParser
import os
import sys

from ipazounds import __version__, locale_dir, zounds

t = gettext.translation('ipazounds', locale_dir, fallback=True)
_ = t.ugettext

def main ():
    """Command line handling."""
    usage = _('usage: %prog [options] LEXICON RULESET')
    version = '%prog ' + __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-b', '--brackets', action='store_const',
                      const='bracket_input', dest='format',
                      help=_('bracket input words'))
    parser.add_option('-d', '--dialect', type='string', metavar='DIALECT',
                      dest='dialect', default=None,
                      help=_('specify DIALECT of output'))
    parser.add_option('-e', '--end-date', type='int', metavar='END DATE',
                      dest='end_date', default=None,
                      help=_('specify END DATE of transformation'))
    parser.add_option('-f', '--file', dest='filename', metavar='FILE',
                      help=_('write output to FILE'))
    parser.add_option('-l', '--omit', action='store_const',
                      const='omit_input', dest='format',
                      help=_('omit input words'))
    parser.add_option('-p', '--history', action='store_const',
                      const='history', dest='format',
                      default='plain',
                      help=_('output transformation history; ignored if -r is specified'))
    parser.add_option('-r', '--reverse', dest='reverse', action='store_true',
                      default=False, help=_('perform reverse derivation'))
    parser.add_option('-s', '--start-date', type='int',
                      metavar='START DATE', dest='start_date', default=None,
                      help=_('specify START DATE of transformation'))
    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error(_('incorrect number of arguments'))
    lexicon = get_lexicon(args[0])
    try:
        rules_parser = get_rules(args[1])
        rules = rules_parser.get_rules(options.start_date, options.end_date,
                                       options.dialect)
    except zounds.ZoundsError, err:
        handle_error(unicode(err))
    variables = rules_parser.get_variables()
    if options.reverse:
        phonotactics = rules_parser.get_phonotactics()
        sce = zounds.ReverseSoundChange(rules, variables, phonotactics)
        # The history format is not supported for reverse
        # transformations.
        if options.format == 'history':
            options.format = ''
    else:
        sce = zounds.SoundChange(rules, variables)
    try:
        for word in sce.transform_lexicon(lexicon):
            if not options.filename:
                print format_output([word], options.format)
    except zounds.ZoundsError, err:
        handle_error(unicode(err))
    if options.filename:
        output = format_output(lexicon, options.format)
        save_output(output, options.filename)

def handle_error (error_message):
    """Print error message and quit."""
    print error_message.encode('utf-8')
    sys.exit(1)
        
def get_lexicon (lexicon_filename):
    """Return list of words read from file."""
    try:
        words = codecs.open(lexicon_filename, 'rU', 'utf-8').readlines()
    except IOError:
        # Try adding the default lex filename extension.
        if lexicon_filename[-4:] != '.lex' \
               and not os.path.exists(lexicon_filename):
            return get_lexicon('%s.lex' % lexicon_filename)
        message = _('Could not read lexicon file: %s') % sys.exc_info()[1]
        handle_error(message)
    except UnicodeDecodeError:
        message = _('Could not read lexicon file: unable to convert to UTF-8 encoding: %s') % sys.exc_info()[1]
        handle_error(message)
    # Remove BOM if there is one.
    words[0] = words[0].lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
    return zounds.compile_words(words)

def get_rules (rule_filename):
    """Return RulesParser object using lines from file."""
    try:
        rules_file = codecs.open(rule_filename, 'rU', 'utf-8')
    except IOError:
        # Try adding the default sc filename extension.
        if rule_filename[-3:] != '.sc' and not os.path.exists(rule_filename):
            return get_rules('%s.sc' % rule_filename)
        message = _('Could not read rules file: %s') % sys.exc_info()[1]
        handle_error(message)
    except UnicodeDecodeError:
        message = _('Could not read rules file: unable to convert to UTF-8 encoding: %s') % sys.exc_info()[1]
        handle_error(message)
    lines = rules_file.readlines()
    rules_file.close()
    # Remove BOM if there is one.
    lines[0] = lines[0].lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
    return zounds.RulesParser(lines)

def format_output(lexicon, output_format):
    """Format and return the output of the transformation of the
    lexicon."""
    output = []
    if output_format == 'history':
        for word in lexicon:
            if word is word.get_final_derivatives()[0]:
                output.append('%s -> %s' % (word.get_form('display'),
                                            word.get_form('display')))
                continue
            output.append('%s -> %s ( %s )' %
                          (word.get_form('display'),
                           get_derivative_word_form(word),
                           get_derivative_rule_form(word)))
            indent = len(word.get_form('display'))
            word = word.get_derivative()['word']
            while word.get_derivative():
                output.append(' ' * indent + ' -> %s ( %s )'
                              % (get_derivative_word_form(word),
                                 get_derivative_rule_form(word)))
                word = word.get_derivative()['word']
    elif output_format == 'omit_input':
        for word in lexicon:
            for derived in derivatives:
                output.append(derived.get_form('display'))
    elif output_format == 'bracket_input':
        for word in lexicon:
            word_display = word.get_form('display')
            derivatives = word.get_final_derivatives()
            if derivatives:
                for derived in derivatives:
                    output.append('%s [%s]' % (derived.get_form('display'),
                                               word_display))
            else:
                output.append('  [%s]' % word_display)
    else:
        for word in lexicon:
            word_display = word.get_form('display')
            derivatives = word.get_final_derivatives()
            if derivatives:
                for derived in derivatives:
                    output.append('%s --> %s' % (word_display,
                                                 derived.get_form('display')))
            else:
                output.append('%s -->' % word_display)
    return '\n'.join(output)

def get_derivative_word_form (word):
    """Return the display form of the immediate derivative word of
    word."""
    return word.get_derivative()['word'].get_form('display')

def get_derivative_rule_form (word):
    """Return the display form of the immediate derivative rule of
    word."""
    return word.get_derivative()['rule'].get_unformatted()

def save_output (output, filename):
    """Save output to filename.

    Arguments:
    output -- string of output
    filename -- string filename to write to
    """
    try:
        output_file = open(filename, 'w')
        output_file.write(output)
        output_file.close()
    except IOError:
        message = _('Could not save results to file: %s') % sys.exc_info()[1]
        handle_error(message)
        

if __name__ == "__main__":
    main()
