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

"""This module contains classes for the IPA part of IPA Zounds."""

import gettext
from ipazounds import locale_dir, zounds, convert

t = gettext.translation('ipazounds', locale_dir, fallback=True)
_ = t.ugettext


class SoundChange (zounds.SoundChange):
    """Interface to the Zounds engine which handles IPA input and
    output."""

    def __init__ (self, rules):
        zounds.SoundChange.__init__(self, rules)
        self.__current_replacement = ''

    def __apply_rule (self, word, rule):
        """Return Word object derived from applying rule to word."""
        regexp = rule.get_reg_exp()
        self.__current_replacement = rule.get_component('result', 'work')
        try:
            result = regexp.subn(self.__modify_features, self.__word_form)
        except zounds.InvalidRuleError, err:
            raise zounds.InvalidRuleError(rule, err.problem)
        if result[1]:
            new_word = Word(result[0])
            word.set_derivative(rule, new_word)
            self.__word_form = new_word.get_form('work')
            return new_word
        return word

    def __modify_features (self, match):
        """Modify features of string in match object."""
        replacement = []
        index = 0
        source = self.__current_replacement.replace('[01]', '2')
        # Jump through the source string, dealing with each
        # significant character or group of characters.
        while index < len(source):
            char = source[index]
            if char in (convert.NFPM, '0', '1'):
                replacement.append(char)
            elif char == '2':
                try:
                    replacement.append(match.group('match')[index])
                except IndexError:
                    raise zounds.InvalidRuleError(None, _('insertion of multiple phonemes via binary features set in rule %s is not permitted'))
            elif char == '(':
                # This is a homorganic variable reference which
                # consists of more than one character. We are only
                # interested in the group name, not the regular
                # expression syntax - (\g< and ?) - around it.
                remainder = source[index:]
                rab_index = remainder.find('>')
                homorganic_variable = remainder[4:rab_index]
                try:
                    replacement.append(match.group(homorganic_variable))
                except IndexError:
                    raise zounds.InvalidRuleError(None,
                                                  _('in %s homorganic variable referenced in result component but not defined in environment component'))
                # Replace the homorganic variable substring (more than
                # one character) with a single character so that the
                # indexing will continue to synch between source and
                # the match object's groups.
                source = '%s %s' % (source[:index], source[index+rab_index+2:])
            index = index + 1
        return match.group('start') + ''.join(replacement)


class ReverseSoundChange (zounds.ReverseSoundChange):
    """Class for performing reverse sound changes on a lexicon."""

    def __init__ (self, rules, phonotactics={}):
        zounds.ReverseSoundChange.__init__(self, rules, {}, phonotactics)
        self.__current_replacement = ''

    def __make_pattern (self, syllable_structures):
        """Return regular expression pattern derived from syllable_structures.

        Arguments:
        syllable_structures -- list of strings in rule format

        """
        if not syllable_structures:
            return ''
        syllable_structures = [converter.ipa_to_script('(<+sb>)' + structure,
                                                       'normalised')
                               for structure in syllable_structures]
        return zounds.ReverseSoundChange.__make_pattern(self,
                                                        syllable_structures)

    def transform_lexicon (self, words):
        """Transform words.

        Arguments:
        words -- list of Word objects.
        
        """
        new_words = []
        for word in words:
            word.clear_derivatives()
            word.length = len(word.get_form('work'))
            word.gs_source(word)
            input_words = [word]
            for rule in self.__rules:
                # Create a SoundChange object in order to check the
                # reverse derived words - it is possible to reverse derive
                # a word which does not derive into the original using the
                # same rule.
                sce = SoundChange([rule.get_reverse_rule()])
                new_words = []
                for input_word in input_words:
                    length = input_word.gs_source().length
                    new_words.extend(self.__transform_word(input_word, rule,
                                                           sce, length))
                input_words = new_words
            for final_word in new_words:
                # Ensure that, if syllable structures have been defined,
                # that all of the derived words conform to them.
                final_form = final_word.get_form('work')
                if self.__check_word_shape(final_form):
                    final_word.gs_source().add_final_derivative(final_word)
            yield word

    def __transform_word (self, word, rule, sce, length):
        """Transform word according to rule, using partial
        matching. Check each derived word for validity using sce.

        Arguments:
        word -- Word object
        rule -- Rule object
        sce -- SoundChange object initialised with rule
        length -- integer length of source word for word
        
        """
        max_length = 1.5 * length
        new_words = []
        seen_words = []
        for new_word in self.__apply_rule(word, rule):
            # Don't bother with words which are much longer than the
            # source.
            new_length = len(new_word)
            if (new_length >= max_length and new_length > 8) or \
               (new_length < 9 and new_length > length + 4):
                continue
            # Ensure that we don't have duplicate words.
            if new_word in seen_words:
                continue
            seen_words.append(new_word)
            word_obj = Word(new_word)
            # Only include those derived words which transform back
            # into the starting word.
            for word_obj in sce.transform_lexicon([word_obj]):
                if word_obj.get_final_derivatives()[0] == word:
                    word_obj.gs_source(word.gs_source())
                    new_words.append(word_obj)
        return new_words

    def __apply_rule (self, word, rule):
        """Return Word objects derived from partial applications of
        rule to word."""
        regexp = rule.get_reg_exp()
        self.__current_replacement = rule.get_component('result', 'work')
        word_form = word.get_form('work')
        words = ['']
        index = 0
        # Sometimes a pattern can keep matching forever when iterated
        # over (eg, /m/_#), so get a count of how many there are in a
        # single pass, and don't do more than that.
        length = len(regexp.findall(word_form))
        i = 1
        for match in regexp.finditer(word_form):
            if i > length:
                break
            part = word_form[index:match.start()]
            try:
                words = self.__make_variants(words, match, part,
                                             self.__get_replacement(match))
            except zounds.InvalidRuleError, err:
                raise zounds.InvalidRuleError(rule, err.problem)
            index = match.end()
            i = i + 1
        else:
            words = [word + word_form[index:] for word in words]
        if len(words) < 2:
            words = [word_form]
        return words

    def __get_replacement (self, match):
        """Return replacement string from match object."""
        replacement = []
        index = 0
        source = self.__current_replacement.replace('[01]', '2')
        # Jump through the source string, dealing with each
        # significant character.
        while index < len(source):
            char = source[index]
            if char in (convert.NFPM, '0', '1'):
                replacement.append(char)
            elif char == '2':
                try:
                    replacement.append(match.group('match')[index])
                except IndexError:
                    raise zounds.InvalidRuleError(None, _('insertion of multiple phonemes via binary features set in (reversed) rule %s is not permitted'))
            elif char == '(':
                # This is a homorganic variable reference, which is
                # not permitted in the reverse applier.
                raise zounds.InvalidRuleError(None,
                                              _('homorganic variable in %s is not permitted in reverse applier'))
            index = index + 1
        return ''.join(replacement)


class Display:
    """Class for handling the displaying of input and output of IPA
    Zounds."""

    def __init__ (self, script='ipa'):
        self.__current_script = script
        self.__output_format = None
        self.__full_format = False

    def get_current_script (self):
        """Return the name of the current script."""
        return self.__current_script

    def set_current_script (self, script):
        """Set the current script to script."""
        self.__current_script = script

    def set_full_format (self, full_format):
        """Set full format attribute, determining whether to fully
        format rules or not."""
        self.__full_format = full_format

    def set_output_format (self, output_format):
        """Set output format attribute."""
        self.__output_format = output_format

    def get_formatted_output (self, lexicon):
        """Format and return the output of the transformation of the
        lexicon."""
        output = []
        if self.__output_format == 'history':
            for word in lexicon:
                display_word = word.get_form('display')
                if word is word.get_final_derivatives()[0]:
                    output.append(u"%s \N{RIGHTWARDS ARROW} %s" % (display_word,
                                                                   display_word))
                    continue
                derivative = word.get_derivative()
                derived_display_word = derivative['word'].get_form('display')
                derived_display_rule = derivative['rule'].get_formatted(self.__full_format)
                output.append(u'%s \N{RIGHTWARDS ARROW} %s %s' %
                              (display_word, derived_display_word,
                               self.__format_history_rule(derived_display_rule,
                                                          len(display_word) +
                                                          len(derived_display_word))))
                indent = len(display_word)
                word = word.get_derivative()['word']
                derivative = word.get_derivative()
                while derivative:
                    display_word = derivative['word'].get_form('display')
                    display_rule = derivative['rule'].get_formatted(self.__full_format)
                    output.append(' ' * indent + u' \N{RIGHTWARDS ARROW} %s %s'
                                  % (display_word,
                                     self.__format_history_rule(display_rule,
                                                                indent +
                                                                len(display_word))))
                    word = word.get_derivative()['word']
                    derivative = word.get_derivative()
        elif self.__output_format == 'omit_input':
            for word in lexicon:
                for derived in word.get_final_derivatives():
                    output.append(derived.get_form('display'))
        elif self.__output_format == 'bracket_input':
            for word in lexicon:
                word_display = word.get_form('display')
                derivatives = word.get_final_derivatives()
                if derivatives:
                    for derived in derivatives:
                        derived_display = derived.get_form('display')
                        output.append(u'%s [%s]' % (derived_display,
                                                    word_display))
                else:
                    output.append(u'\N{EMPTY SET} [%s]' % word_display)
        else:
            for word in lexicon:
                word_display = word.get_form('display')
                derivatives = word.get_final_derivatives()
                if derivatives:
                    for derived in derivatives:
                        output.append(u'%s \N{RIGHTWARDS ARROW} %s' %
                                      (word_display,
                                       derived.get_form('display')))
                else:
                    output.append(u'%s \N{RIGHTWARDS ARROW} \N{EMPTY SET}' %
                                  word_display)
        return output

    def __format_history_rule (self, rule, indent):
        """Return a properly formatted string of rule for history output."""
        if len(rule) == 1:
            return '( ' + ''.join(rule) + ' )'
        else:
            # Add four spaces due to spaces between words in history output
            indent = '\n' + ' ' * (indent + 4)
            for i in range(len(rule)):
                if i == 0:
                    fmt_rule = u'\N{LEFT PARENTHESIS UPPER HOOK} %s \N{RIGHT PARENTHESIS UPPER HOOK}' \
                              % rule[i]
                elif i == len(rule) - 1:
                    fmt_rule = fmt_rule + u'%s\N{LEFT PARENTHESIS LOWER HOOK} %s \N{RIGHT PARENTHESIS LOWER HOOK}' \
                              % (indent, rule[i])
                else:
                    fmt_rule = fmt_rule + u'%s\N{LEFT PARENTHESIS EXTENSION} %s \N{RIGHT PARENTHESIS EXTENSION}' \
                              % (indent, rule[i])
        return fmt_rule

    
display = Display()


class Rule (zounds.Rule):
    """Class for handling a sound change rule."""

    __display = display
    
    def __init__ (self, rule, date=None, dialects=(), script='ipa'):
        self.__rule = rule
        self.__script = script
        self.__script_form = {}
        zounds.Rule.__init__(self, self.__rule, date, dialects)
        self.__fully_formatted = {}
        self.__partially_formatted = {}
        self.__formatted_components = {}

    def _get_divider (self):
        """Return the string used to divide rule components."""
        if self.__script == 'ipa':
            return '/'
        else:
            return converter.get_rule_divider(self.__script)

    def get_component (self, component, form):
        """Return value of component in form."""
        if form == 'display':
            return self.__get_script_form(component,
                                          self.__display.get_current_script())
        elif form == 'work':
            return self.__get_script_form(component, 'normalised')

    def __get_script_form (self, component, script_form):
        """Return component in script form, deriving it if
        necessary."""
        if not self.__script_form.has_key(script_form):
            # Derive and set the script form.
            if script_form == self.__script:
                self.__script_form[script_form] = self.__original_components
            elif script_form == 'normalised':
                self.__script_form[script_form] = self.__normalise_rule()
            elif script_form == 'ipa':
                source = converter.script_to_ipa(self.__get_script_form('source', self.__script), self.__script)
                result = converter.script_to_ipa(self.__get_script_form('result', self.__script), self.__script)
                environment = converter.script_to_ipa(self.__get_script_form('environment', self.__script), self.__script)
                self.__script_form[script_form] = {'source': source,
                                                   'result': result,
                                                   'environment': environment}
            else:
                source = converter.ipa_to_script(self.__get_script_form('source', 'ipa'), script_form)
                result = converter.ipa_to_script(self.__get_script_form('result', 'ipa'), script_form)
                environment = converter.ipa_to_script(self.__get_script_form('environment', 'ipa'), script_form)
                self.__script_form[script_form] = {'source': source,
                                                   'result': result,
                                                   'environment': environment}
        return self.__script_form[script_form][component]

    def _check_result_component (self, result):
        """Check that the result component of rule is valid."""
        zounds.Rule._check_result_component(self, result)
        # This check must be done on the ipa rule's result
        # component, not the normalised version (which may have angle
        # brackets as part of the generated regular expression
        # syntax).
        component = self.__get_script_form('result', 'ipa')
        if '<' in component:
            raise zounds.InvalidRuleError(self, _("Result component of rule %s may not contain angle brackets ('<' or '>')"))
        if '>' in component:
            raise zounds.InvalidRuleError(self, _("Result component of rule %s may not contain angle brackets ('<' or '>')"))

    def _check_source_component (self, source):
        """Check that the source component of a rule is valid."""
        zounds.Rule._check_source_component(self, source)
        component = self.__get_script_form('source', 'ipa')
        open_sb = False
        for char in component:
            if char == '[':
                open_sb = True
            elif char in convert.homorganic_variables.keys():
                if open_sb:
                    raise zounds.InvalidRuleError(self, _('Source component of rule %s may not contain homorganic variables (Greek letters)'))
            elif char == ']':
                open_sb = False

    def __normalise_rule (self):
        """Return component converted into normalised form."""
        components = {'source': self.__get_script_form('source', 'ipa'),
                      'result': self.__get_script_form('result', 'ipa'),
                      'environment': self.__get_script_form('environment',
                                                            'ipa')}
        for key, value in components.items():
            try:
                components[key] = converter.ipa_to_script(value, 'normalised')
            except convert.ConvertError, err:
                raise zounds.InvalidRuleError(self,
                                              _('Invalid IPA sequence in %s: ')
                                              + str(err).decode('utf-8'))
        # Replace any homorganic variables with the appropriate
        # regular expression group names.
        for mark in convert.homorganic_variables.values():
            # In the result component, we want to match on what was
            # earlier matched.
            components['result'] = components['result'].replace(mark,
                                                                '(\g<%s>)'
                                                                % mark)
            # In the environment component, we want to name the
            # match.
            components['environment'] = components['environment'].replace(mark,
                                                                          '(?P<%s>[01])' % mark)
        return components

    def get_formatted (self, full_format):
        """Return rule in presentational format, as a list of strings,
        each a line of the formatted rule.

        Arguments:
        full_format -- Boolean indicator of whether to fully format rule

        Full formatting uses vertical positioning of binary features
        and Unicode characters for extended parentheses and
        brackets. It requires a monospace font in order for the
        multiple lines to align correctly.
        
        """
        script_name = self.__display.get_current_script()
        # Minimal formatting
        if not full_format:
            return self.__get_partially_formatted(script_name)
        # Full formatting
        if self.__fully_formatted.has_key(script_name):
            return self.__fully_formatted[script_name]
        components = self.__get_formatted_components(script_name)
        rule_parts = []
        # Define the characters used to mark binary feature sets.
        (lsb, rsb) = self.__get_bf_set_markers(script_name)
        for component in (components['source'], components['result'],
                          components['environment']):
            # Go through each component, compiling a list of elements,
            # either a single non-feature chunk of IPA characters or a
            # list of features modifying the same sound.
            compiled = []
            feature_indent = [0]
            while True:
                try:
                    lsb_index = component.index(lsb)
                    rsb_index = component.index(rsb)
                except ValueError:
                    compiled.append(component)
                    break
                compiled.append(component[:lsb_index])
                feature_set = component[lsb_index+1:rsb_index]
                ipa_indent = len(component[:lsb_index])
                compiled_features = self.__compile_features(feature_set,
                                                            ipa_indent,
                                                            feature_indent)
                compiled.append(compiled_features)
                feature_indent = self.__determine_indent(ipa_indent,
                                                         feature_indent,
                                                         compiled_features)
                component = component[rsb_index+1:]
            compiled = self.__glue_component(compiled)
            rule_parts.append(compiled)
        # Put padded elements in rule components so they all have the
        # same number of elements (lines).
        max_lines = max(len(rule_parts[0]), len(rule_parts[1]),
                        len(rule_parts[2]))
        for i in range(max_lines):
            if len(rule_parts[0]) < i+1:
                rule_parts[0].append(" " * len(rule_parts[0][0]))
            if len(rule_parts[1]) < i+1:
                rule_parts[1].append(" " * len(rule_parts[1][0]))
            if len(rule_parts[2]) < i+1:
                rule_parts[2].append(" " * len(rule_parts[2][0]))
        compiled_rule = []
        # Now join the three rule components together, line by line.
        for i in range(len(rule_parts[0])):
            if i == 0:
                # First line
                compiled_rule.append(u"%s \N{RIGHTWARDS ARROW} %s / %s" % \
                                     (rule_parts[0][0], rule_parts[1][0],
                                      rule_parts[2][0]))
            else:
                # Other lines
                compiled_rule.append(u"%s   %s   %s" % \
                                     (rule_parts[0][i], rule_parts[1][i],
                                      rule_parts[2][i]))
        self.__fully_formatted[script_name] = compiled_rule
        return self.__fully_formatted[script_name]

    def __get_partially_formatted (self, script_name):
        """Return partially formatted rule in script_name."""
        if not self.__partially_formatted.has_key(script_name):
            components = self.__get_formatted_components(script_name)
            self.__partially_formatted[script_name] = [u'%s \N{RIGHTWARDS ARROW} %s / %s'
                                                       % (components['source'],
                                                          components['result'],
                                                          components['environment'])]
        return self.__partially_formatted[script_name]

    def __get_formatted_components (self, script_name):
        """Return rule in script_name split into components with
        Unicode characters substituted."""
        if not self.__formatted_components.has_key(script_name):
            formatted = {}
            unformatted = {'source': self.__get_script_form('source',
                                                            script_name),
                           'result': self.__get_script_form('result',
                                                            script_name),
                           'environment': self.__get_script_form('environment',
                                                                 script_name)}
            for key, value in unformatted.items():
                if unformatted[key] == '':
                    formatted[key] = u'\N{EMPTY SET}'
                else:
                    formatted[key] = value.replace('-', u'\N{MINUS SIGN}')
            self.__formatted_components[script_name] = formatted
        return self.__formatted_components[script_name]

    def __get_bf_set_markers (self, script_name):
        """Return a list of the strings used to mark off sets of
        binary features (opening marker, closing marker)."""
        if script_name == 'ipa':
            return ('[', ']')
        else:
            return converter.get_bf_set_markers(script_name)
        
    def __compile_features (self, feature_set, ipa_indent, feature_indent):
        """Return a list of strings, each a line of a feature list,
        complete with extended brackets.

        Arguments:
        feature_set -- string of set of features        
        ipa_indent -- integer number of characters to indent due to
                      IPA characters between this set of features and
                      any previous set
        feature_indent -- list of integer number of characters to
                          indent due to previous feature set. Index 0
                          integer marks the default, the other
                          indices' integers mark the amount indented
                          on the next line (index 1 gives indent for
                          line 2; line 1 is always indented 0).
        """
        num_features = 0
        length = 1
        max_length = 0
        new_features = []
        feature_signs = [u'\N{MINUS SIGN}', '+']
        feature_signs.extend(convert.homorganic_variables.keys())
        for char in feature_set:
            if char in feature_signs:
                num_features = num_features + 1
                new_features.append(char)
                if length > max_length:
                    max_length = length
                length = 1
                continue
            length = length + 1
            new_features[num_features-1] = new_features[num_features-1] + char
        if length > max_length:
            max_length = length
        # Generic sound with no features
        if not new_features:
            return ['[]']
        if len(new_features) == 1:
            return [u'[%s]' % new_features[0]]
        compiled_rule = []
        # Handle each line of a multiline feature set appropriately
        for i in range(len(new_features)):
            if i == 0:
                compiled_rule.append(u'\N{LEFT SQUARE BRACKET UPPER CORNER}%s%s\N{RIGHT SQUARE BRACKET UPPER CORNER}' % \
                                     (new_features[i-1],
                                      ' ' * (max_length -
                                             len(new_features[i-1]))))
            elif i == len(new_features)-1:
                try:
                    indent = ipa_indent + feature_indent[i]
                except IndexError:
                    indent = ipa_indent + feature_indent[0]
                compiled_rule.append(u'%s\N{LEFT SQUARE BRACKET LOWER CORNER}%s%s\N{RIGHT SQUARE BRACKET LOWER CORNER}' % \
                                     (' ' * indent, new_features[i-1],
                                      ' ' * (max_length -
                                             len(new_features[i-1]))))
            else:
                try:
                    indent = ipa_indent + feature_indent[i]
                except IndexError:
                    indent = ipa_indent + feature_indent[0]
                compiled_rule.append(u'%s\N{LEFT SQUARE BRACKET EXTENSION}%s%s\N{RIGHT SQUARE BRACKET EXTENSION}' % \
                                     (' ' * indent, new_features[i-1],
                                      ' ' * (max_length -
                                             len(new_features[i-1]))))
        return compiled_rule

    def __determine_indent (self, ipa_indent, feature_indent,
                            compiled_features):
        """Return a list of the feature indents for each line based on
        the previous indents and the latest set of features.

        For each of the lines in compiled_features, the new indent is
        0. For lines in feature_indent not covered by
        compiled_features, the indent is the value in feature_indent
        plus the length of the feature block in compiled_features plus
        the ipa_indent. This includes the default from feature_indent.

        """
        feature_length = len(compiled_features[0])
        feature_lines = len(compiled_features)
        feature_indent[0] = feature_indent[0] + feature_length + ipa_indent
        for i in range(1, feature_lines):
            try:
                feature_indent[i] = 0
            except IndexError:
                feature_indent.append(0)
        for i in range(feature_lines, len(feature_indent)):
            feature_indent[i] = feature_indent[i] + feature_length + \
                                ipa_indent
        return feature_indent

    def __glue_component (self, component):
        """Join elements in list component together into list of strings
        (each string a line)."""
        lines = []
        lines.append('')
        for part in component:
            if type(part) == type([]):
                for i in range(len(part)):
                    try:
                        lines[i] = lines[i] + part[i]
                    except IndexError:
                        lines.append(part[i])
            else:
                lines[0] = lines[0] + part
        # Pad out with spaces any lines which are shorter than the first
        # (which is always the longest).
        for i in range(len(lines)):
            if len(lines[i]) < len(lines[0]):
                lines[i] = lines[i] + ' ' * (len(lines[0]) - len(lines[i]))
        return lines


class Word (zounds.Word):
    """Class for handling a lexicon item."""

    __display = display

    def __init__ (self, word, script='normalised'):
        """Arguments:
        word -- string of word
        script -- string of script that word is in

        """
        zounds.Word.__init__(self, word)
        self.__script = script
        self.__script_form = {}

    def get_form (self, form):
        """Return the specified form of self."""
        if form == 'display':
            return self.__get_script_form(self.__display.get_current_script())
        elif form == 'work':
            return self.__get_script_form('normalised')

    def __get_script_form (self, script_form):
        """Return the word in script_form, deriving it if necessary."""
        if not self.__script_form.has_key(script_form):
            # Derive and set the script form.
            if script_form == self.__script:
                self.__script_form[script_form] = self.__original
            elif script_form == 'ipa':
                self.__script_form[script_form] = converter.script_to_ipa(self.__original, self.__script)
            else:
                self.__script_form[script_form] = converter.ipa_to_script(self.__get_script_form('ipa'), script_form)
        return self.__script_form[script_form]


class RulesParser (zounds.RulesParser):

    """Class for parsing the contents of a rules file."""

    def __init__ (self, lines, script='ipa'):
        self.__script = script
        zounds.RulesParser.__init__(self, lines, Rule)

    def _parse_groups_section (self, lines):
        """Parse the groups section content in lines."""
        self._section_lines['Groups'] = []
        group = None
        for line in lines:
            if line.startswith('Group '):
                group = line[6:]
                self._groups[group] = []
                self._section_lines['Groups'].append(line)
            else:
                # Check that the line is a valid rule, by making a
                # temporary Rule object from it.
                rule = self._Rule(line, script=self.__script)
                self._section_lines['Groups'].append(rule)
                rule = None
                try:
                    # Only record the line, not the Rule object, because
                    # the rule may be used in many different contexts.
                    self._groups[group].append(line)
                except KeyError:
                    raise zounds.InvalidRulesFileError(_('Invalid content outside of rule group definition'))

    def _parse_persistent_section (self, lines):
        """Parse the persistent rules section content in lines."""
        self._section_lines['Persistent'] = []
        for line in lines:
            parts = line.split(' ')
            if len(parts) == 1:
                # Check for group reference.
                if self._groups.has_key(line):
                    self._section_lines['Persistent'].append(line)
                    for rule in self._groups[line]:
                        self._persistent.append(self._Rule(rule,
                                                           script=self.__script))
                else:
                    rule = self._Rule(parts[0], script=self.__script)
                    self._persistent.append(rule)
                    self._section_lines['Persistent'].append(rule)
            elif len(parts) == 2:
                dialects = self._parse_dialects(parts[1])
                if self._groups.has_key(parts[0]):
                    self._section_lines['Persistent'].append((parts[0],
                                                              dialects))
                    for group_rule in self._groups[parts[0]]:
                        self._persistent.append(self._Rule(group_rule,
                                                           None, dialects,
                                                           self.__script))
                else:
                    rule = self._Rule(rule, None, dialects, self.__script)
                    self._persistent.append(rule)
                    self._section_lines['Persistent'].append((rule, dialects))
            else:
                message = _('Malformed line (%s) in persistent rule section: no spaces are allowed in the either the rule or dialect parts')
                raise zounds.InvalidRulesFileError(message, line)

    def _parse_rules_section (self, lines):
        """Parse the rules section content in lines."""
        self._section_lines['Rules'] = []
        if not lines:
            message = _('At least one rule must be specified in the rules section')
            raise zounds.InvalidRulesFileError(message)
        date = None
        for line in lines:
            parts = line.split(' ')
            if len(parts) == 1:
                try:
                    new_date = int(line)
                except ValueError:
                    if self._groups.has_key(line):
                        self._section_lines['Rules'].append(line)
                        group = []
                        for rule in self._groups[parts[0]]:
                            group.append(self._Rule(rule, date,
                                                    script=self.__script))
                        self._rules.append(group)
                    else:
                        rule = self._Rule(parts[0], date, script=self.__script)
                        self._rules.append(rule)
                        self._section_lines['Rules'].append(rule)
                else:
                    if date is not None and new_date <= date:
                        message = _('Date %s is not later than the previously specified date')
                        raise zounds.InvalidRulesFileError(message, line)
                    else:
                        date = new_date
                        self._section_lines['Rules'].append(date)
                        self._dates.append(date)
            elif len(parts) == 2:
                dialects = self._parse_dialects(parts[1])
                if self._groups.has_key(parts[0]):
                    self._section_lines['Rules'].append((parts[0], dialects))
                    group = []
                    for rule in self._groups[parts[0]]:
                        group.append(self._Rule(rule, date, dialects,
                                                self.__script))
                    self._rules.append(group)
                else:
                    rule = self._Rule(parts[0], date, dialects, self.__script)
                    self._rules.append(rule)
                    self._section_lines['Rules'].append((rule, dialects))
            else:
                message = _('Malformed line (%s) in rule section: no spaces are allowed in either the rule or dialect parts')
                raise zounds.InvalidRulesFileError(message, line)


def compile_words (lexicon, script='ipa'):
    """Return list of word objects created from list of word strings."""
    words = []
    for word in lexicon:
        word = word.strip()
        if word:
            words.append(Word(word, script))
    return words
 

converter = convert.Converter()
