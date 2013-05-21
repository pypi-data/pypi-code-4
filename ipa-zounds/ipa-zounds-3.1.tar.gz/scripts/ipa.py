#!/usr/bin/env python

# IPA Zounds, a sound change engine with support for the IPA.
# Copyright (C) 2003 Jamie Norrish
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
# along with IPA Zounds; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""This is the IPA command line program for IPA Zounds."""

import codecs
import gettext
from optparse import OptionParser
import os
import sys

from ipazounds import __version__, locale_dir, ipa, zounds

t = gettext.translation('ipazounds', locale_dir, fallback=True)
_ = t.ugettext

def main ():
    """Command line handling."""
    usage = 'usage: %prog [options] LEXICON RULESET'
    version = '%prog ' + __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-b', '--brackets', action='store_const',
                      const='bracket_input', dest='format',
                      help=_('bracket input words'))
    parser.add_option('-d', '--dialect', type='string', metavar='DIALECT',
                      dest='dialect', default=None,
                      help=_('specify DIALECT (abbreviated form) of output'))
    parser.add_option('-e', '--end-date', type='int', metavar='END DATE',
                      dest='end_date', default=None,
                      help=_('specify END DATE of transformation'))
    parser.add_option('-f', '--file', dest='filename', metavar='FILE',
                      type='string', help=_('write output to FILE'))
    parser.add_option('-l', '--omit', action='store_const',
                      const='omit_input', dest='format',
                      help=_('omit input words'))
    parser.add_option('-m', '--max-format', action='store_true',
                      dest='full_format', default=False,
                      help=_('format rules fully if -p used'))
    parser.add_option('-o', '--output-script', type='string', metavar='SCRIPT',
                      dest='output_script', default='ipa',
                      help=_('show output written in SCRIPT'))
    parser.add_option('-p', '--history', action='store_const',
                      const='history', dest='format',
                      default='plain', help=_('output transformation history'))
    parser.add_option('-r', '--rule-script', type='string', dest='rule_script',
                      metavar='SCRIPT', default='ipa',
                      help=_('specify RULESET is written in SCRIPT'))
    parser.add_option('-s', '--start-date', type='int',
                      metavar='START DATE', dest='start_date', default=None,
                      help=_('specify START DATE of transformation'))
    parser.add_option('-v', '--reverse', dest='reverse', action='store_true',
                      default=False, help=_('perform reverse derivation'))
    parser.add_option('-w', '--word-script', type='string', dest='word_script',
                      metavar='SCRIPT', default='ipa',
                      help=_('specify LEXICON is written in SCRIPT'))
    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error('incorrect number of arguments')
    lexicon = get_lexicon(args[0], options.word_script)
    try:
        rules_parser = get_rules(args[1], options.rule_script)
        rules = rules_parser.get_rules(options.start_date, options.end_date,
                                       options.dialect)
    except zounds.ZoundsError, err:
        handle_error(unicode(err))
    ipa.display.set_current_script(options.output_script)
    ipa.display.set_output_format(options.format)
    ipa.display.set_full_format(options.full_format)
    if options.reverse:
        phonotactics = rules_parser.get_phonotactics()
        sce = ipa.ReverseSoundChange(rules, phonotactics)
        # The history format is not supported for reverse
        # transformations.
        if options.format == 'history':
            ipa.display.set_output_format('')
    else:
        sce = ipa.SoundChange(rules)
    try:
        for word in sce.transform_lexicon(lexicon):
            if not options.filename:
                try:
                    output = '\n'.join(ipa.display.get_formatted_output([word])).encode('utf-8')
                except ipa.convert.InvalidCharError, err:
                    handle_error(unicode(err))
                if output:
                    print output
    except zounds.ZoundsError, err:
        handle_error(unicode(err))
    if options.filename:
        output = '\n'.join(ipa.display.get_formatted_output(lexicon))
        save_output(output, options.filename)

def handle_error (error_message):
    """Print error message and quit."""
    print error_message.encode('utf-8')
    sys.exit(1)
        
def get_lexicon (lexicon_filename, script):
    """Return list of words read from file."""
    try:
        words = codecs.open(lexicon_filename, 'rU', 'utf-8').readlines()
    except IOError:
        # Try adding the default lex filename extension.
        if lexicon_filename[-4:] != '.lex' \
               and not os.path.exists(lexicon_filename):
            return get_lexicon('%s.lex' % lexicon_filename, script)
        message = _('Could not read lexicon file: %s') % (sys.exc_info()[1])
        handle_error(message)
    except UnicodeDecodeError:
        message = _('Could not read lexicon file: unable to convert to UTF-8 encoding: %s') % sys.exc_info()[1]
        handle_error(message)
    # Remove BOM if there is one.
    words[0] = words[0].lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
    return ipa.compile_words(words, script)

def get_rules (rule_filename, script):
    """Return list of rules read from file."""
    rules = []
    try:
        rules = codecs.open(rule_filename, 'rU', 'utf-8').readlines()
    except IOError:
        # Try adding the default sc filename extension.
        if rule_filename[-3:] != '.sc' and not os.path.exists(rule_filename):
            return get_rules('%s.sc' % rule_filename, script)
        message = _('Could not read rules file: %s') % sys.exc_info()[1]
        handle_error(message)
    except UnicodeDecodeError:
        message = _('Could not read rules file: unable to convert to UTF-8 encoding: %s') % sys.exc_info()[1]
        handle_error(message)
    # Remove BOM if there is one.
    rules[0] = rules[0].lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
    return ipa.RulesParser(rules, script)

def save_output (output, filename):
    """Save output to filename.

    Arguments:
    output -- string of output
    filename -- string filename to write to
    """
    try:
        output_file = codecs.EncodedFile(open(filename, 'w'), 'utf-8')
        output_file.write(output.encode('utf-8'))
        output_file.close()
    except IOError:
        message = _("Could not save results to file: %s") % sys.exc_info()[1]
        handle_error(message)
    

if __name__ == '__main__':
    main()
