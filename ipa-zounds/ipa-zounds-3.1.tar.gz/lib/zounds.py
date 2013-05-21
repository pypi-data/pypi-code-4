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
# along with Foobar; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""This module contains classes for the Zounds part of IPA Zounds."""

import gettext
import re
from ipazounds import locale_dir

t = gettext.translation('ipazounds', locale_dir, fallback=True)
_ = t.ugettext

initial_syllable = 'INITIAL_SYLLABLE'
medial_syllable = 'MEDIAL_SYLLABLE'
final_syllable = 'FINAL_SYLLABLE'

# Define exceptions
class ZoundsError (Exception):
    """Base exception class for Zounds errors."""
    def __init__ (self, problem):
        Exception.__init__(self)
        self.problem = problem.encode('utf-8')

    def __unicode__ (self):
        return self.__str__().decode('utf-8')

class InvalidVariableError (ZoundsError):
    """Exception class for invalid variables."""
    def __init__ (self, varName, varValue, problem):
        ZoundsError.__init__(self, problem)
        self.var = '%s=%s'.encode('utf-8') % (varName, varValue)

    def __str__ (self):
        return self.problem % self.var

class InvalidRulesFileError (ZoundsError):
    """Exception class for invalid rules file."""
    def __init__ (self, problem, *args):
        ZoundsError.__init__(self, problem)
        self.args = tuple([str(arg).encode('utf-8') for arg in args])

    def __str__ (self):
        if self.args:
            return self.problem % self.args
        else:
            return self.problem

class InvalidSectionError (InvalidRulesFileError):
    """Exception class for invalid section in rules file."""
    def __init__ (self, problem, section, line_number=None):
        InvalidRulesFileError.__init__(self, problem, section, line_number)

class InvalidRulesSetError (ZoundsError):
    """Exception class for invalid rulesets in modified transformations."""
    def __init__ (self, problem):
        ZoundsError.__init__(self, problem)

    def __str__ (self):
        return self.problem

class InvalidRuleError (ZoundsError):
    """Exception class for invalid/malformed rules."""
    def __init__ (self, rule, problem):
        ZoundsError.__init__(self, problem)
        self.rule = rule

    def __str__ (self):
        return self.problem % self.rule.get_unformatted().encode('utf-8')

class InvalidWordError (ZoundsError):
    """Exception class for invalid/malformed words."""
    def __init__ (self, word, problem):
        ZoundsError.__init__(self, problem)
        self.word = word

    def __str__ (self):
        return self.problem % self.word.encode('utf-8')

class InvalidWordFormError (ZoundsError):
    """Exception class for invalid word forms."""
    def __init__ (self, word, form, problem):
        ZoundsError.__init__(self, problem)
        self.word = word
        self.form = form

    def __str__ (self):
        return self.problem % (self.word.encode('utf-8'),
                               self.form.encode('utf-8'))

class InvalidSyllableError (ZoundsError):
    """Exception class for invalid syllable definitions."""
    def __init__ (self, problem):
        ZoundsError.__init__(self, problem)

    def __str__ (self):
        return self.problem

class MismatchedVariablesError (ZoundsError):
    """Exception class for variables with differing numbers of
    elements."""
    def __init__ (self, var1, var2, rule, problem):
        ZoundsError.__init__(self, problem)
        self.var1 = var1.encode('utf-8')
        self.var2 = var2.encode('utf-8')
        self.rule = rule

    def __str__ (self):
        return self.problem % (self.var1, self.var2,
                               self.rule.get_unformatted().encode('utf-8'))


class SoundChange:
    """Apply sound-change rules to a lexicon."""

    def __init__ (self, rules, variables={}):
        """Arguments:
        rules -- list of rule objects
        variables -- optional dictionary of variables

        """
        # It is assumed that variables contain Unicode strings (not
        # encoded).
        self.__vars = variables
        self.__check_variables()
        self.__rules = rules
        self.__word_form = ''

    def __check_variables (self):
        """Check that the variables are well formed."""
        for var in self.__vars.keys():
            # Variables may not be empty.
            if not self.__vars[var]:
                raise InvalidVariableError(var, self.__vars[var],
                                           _('variable %s is empty'))
            # Square brackets are illegal.
            if '[' in self.__vars[var] or ']' in self.__vars[var]:
                raise InvalidVariableError(var, self.__vars[var],
                                           _('variable %s contains square bracket'))
            # Variable names must be a single character.
            if len(var) != 1:
                raise InvalidVariableError(var, self.__vars[var],
                                           _('name of variable %s is too long (must be a single character)'))

    def __apply_rule (self, word, rule):
        """Return Word object derived from applying rule to word."""
        rule_result = rule.get_component('result', 'work')
        rule_source = rule.get_component('source', 'work')
        regexp = rule.get_reg_exp(self.__vars)
        original_word_form = self.__word_form
        result = regexp.subn('\g<start>%s' % (rule_result), self.__word_form)
        # Handle the case where a variable is replaced by a variable.
        if result[1] and self.__vars.has_key(rule_result) \
               and self.__vars.has_key(rule_source):
            for match in regexp.finditer(self.__word_form):
                index = self.__vars[rule_source].index(match.group('match'))
                try:
                    # Change the pattern for each match so that
                    # only one element in a variable is replaced
                    # by its match in the corresponding
                    # variable. Eg 'a' in [abc] matches 'd' in
                    # [def].
                    pattern = regexp.pattern.replace('[%s]' %
                                                     self.__vars[rule_source],
                                                     match.group('match'))
                    result = re.subn(pattern, '\g<start>%s' %
                                     (self.__vars[rule_result][index]),
                                     self.__word_form)
                    self.__word_form = result[0]
                except IndexError:
                    raise MismatchedVariablesError(rule_result, rule_source,
                                                   rule,
                                                   _('variable %s has fewer components than variable %s, used in rule %s'))
        # It might be expected that 'if result[1]' is the correct test
        # here, but it doesn't cope with the case of a variable being
        # substituted with a variable, where it does not always
        # match. Therefore, just check that the final word is not the
        # same as the initial.
        if result[0] != original_word_form:
            new_word = Word(result[0])
            word.set_derivative(rule, new_word)
            self.__word_form = new_word.get_form('work')
            return new_word
        return word

    def __transform_word (self, word):
        """Transform word according to all matching rules."""
        self.__word_form = word.get_form('work')
        for rule in self.__rules:
            word = self.__apply_rule(word, rule)
        return word

    def transform_lexicon (self, words):
        """Transform words.

        Arguments:
        words -- list of Word objects.
        
        """
        for word in words:
            word.clear_derivatives()
            final_derivative = self.__transform_word(word)
            word.add_final_derivative(final_derivative)
            yield word


class ReverseSoundChange:
    """Class for performing reverse sound changes on a lexicon."""

    def __init__ (self, rules, variables={}, phonotactics={}):
        """Arguments:
        rules -- list of rule objects
        variables -- optional dictionary of variables
        phonotactics -- optional dictionary of phonotactic variables

        """
        self.__vars = variables
        self.__phonotactics = phonotactics
        self.__word_regexps = self.__create_word_regexps()
        self.__rules = [rule.get_reverse_rule() for rule in rules]
        self.__rules.reverse()

    def __create_word_regexps (self):
        """Return a list of compiled regular expression objects to
        express the possible phonemic composition of a word."""
        # Only MEDIAL_SYLLABLE variable needs to be defined in order
        # for a pattern to be made.
        if self.__phonotactics.get(medial_syllable):
            initial_pattern = self.__make_pattern(self.__phonotactics[initial_syllable])
            medial_pattern = self.__make_pattern(self.__phonotactics[medial_syllable])
            final_pattern = self.__make_pattern(self.__phonotactics[final_syllable])
            if not initial_pattern:
                initial_pattern = medial_pattern
            if not final_pattern:
                final_pattern = medial_pattern
            full_shape = '^%s(%s)*%s$' % (initial_pattern, medial_pattern,
                                          final_pattern)
            initial_shape = '^%s$' % initial_pattern
            final_shape = '^%s$' % final_pattern
            try:
                return (re.compile(full_shape), re.compile(initial_shape),
                        re.compile(final_shape))
            except:
                raise InvalidSyllableError(_('Invalid syllable definition.'))
        return None

    def __make_pattern (self, syllable_structures):
        """Return regular expression pattern derived from syllable_structures.

        Arguments:
        syllable_structures -- list of strings in rule format

        """
        if not syllable_structures:
            return ''
        patterns = []
        for structure in syllable_structures:
            pattern = ['(']
            for char in structure:
                if char == ')':
                    pattern.append(')?')
                elif self.__vars.has_key(char):
                    pattern.append('[' + self.__vars[char] + ']')
                else:
                    pattern.append(char)
            pattern.append(')')
            patterns.append(''.join(pattern))
        return '(' + '|'.join(patterns) + ')'

    def __check_word_shape (self, word):
        """Return True if word matches phonotactic requirements, False
        otherwise."""
        if not word:
            return False
        if not self.__word_regexps:
            return True
        if self.__word_regexps[0].search(word):
            return True
        if self.__word_regexps[1].search(word) and \
           self.__word_regexps[2].search(word):
            return True
        return False

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
                sce = SoundChange([rule.get_reverse_rule()], self.__vars)
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
        rule_result = rule.get_component('result', 'work')
        rule_source = rule.get_component('source', 'work')
        regexp = rule.get_reg_exp(self.__vars)
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
            if self.__vars.has_key(rule_result) and \
                   self.__vars.has_key(rule_source):
                # Substitution of one variable with another.
                try:
                    index = self.__vars[rule_source].index(match.group('match'))
                except IndexError:
                    raise MismatchedVariablesError(rule_result, rule_source,
                                                   rule, _('variable %s has fewer components than variable %s, used in rule %s'))
                replacement = self.__vars[rule_result][index]
            elif self.__vars.has_key(rule_result):
                # Substitution of non-variable with variable.
                replacement = [self.__vars[rule_result]]
            else:
                replacement = rule_result
            words = self.__make_variants(words, match, part, replacement)
            index = match.end()
            i = i + 1
        else:
            words = [word + word_form[index:] for word in words]
        if len(words) < 2:
            words = [word_form]
        return words

    def __make_variants (self, words, match, part, replacement):
        """Return list of word parts built from existing word parts,
        the part before the current match, and both the match and
        replacement.

        Arguments:
        words -- list of existing word parts
        match -- regular expression match object
        part -- string of original word before match and after the
                previous match
        replacement -- replacement text (usually a string; may be a
                       list when there is variable substitution)

        """
        new_words = []
        for word in words:
            # First add the original, unchanged word segment.
            new_words.append(''.join((word, part, match.group())))
            if type(replacement) == type([]):
                for char in replacement[0]:
                    new_words.append(''.join((word, part, match.group('start'),
                                              char)))
            else:
                new_words.append(''.join((word, part, match.group('start'),
                                          replacement)))
        return new_words
    

class Rule:
    """Class for handling a sound change rule."""
    def __init__ (self, rule, date=None, dialects=()):
        self.__rule = rule
        self.__date = date
        self.__dialects = dialects
        self.__original_components = self.__divide_rule(self.__rule)
        self.__components = {}
        self.__check_components()
        self.__regexp = None

    def get_unformatted (self):
        """Return the unformatted form of rule."""
        return self.__rule

    def get_reverse_rule (self):
        """Return new Rule object representing the reverse of self."""
        source = self.__original_components['result']
        result = self.__original_components['source']
        environment = self.__original_components['environment']
        rule = '/'.join((source, result, environment))
        return self.__class__(rule, self.__date, self.__dialects)

    def get_dialects (self):
        """Return list of dialects that apply to self."""
        return self.__dialects

    def get_date (self):
        """Return date associated with self."""
        return self.__date

    def __check_components (self):
        """Run a series of validity checks on the rule components."""
        source = self.get_component('source', 'work')
        result = self.get_component('result', 'work')
        environment = self.get_component('environment', 'work')
        self._check_source_component(source)
        self._check_result_component(result)
        self._check_environment_component(environment)
        for component in (source, result, environment):
            self.__check_mismatched_brackets(component)
            self.__check_asterisk_without_parenthesis(component)

    def _check_source_component (self, source):
        """Check that the source component of rule is valid."""
        pass

    def _check_result_component (self, result):
        """Check that the result component of the rule is valid."""
        if '*' in result:
            raise InvalidRuleError(self, _("result component of rule %s contains an invalid character ('*' is not permitted"))

    def _check_environment_component (self, env):
        """Check that the environment component env of rule is valid."""
        if '_' not in env:
            raise InvalidRuleError(self, _("environment component of rule %s has no phoneme placeholder ('_')"))
        if env.count('_') > 1:
            raise InvalidRuleError(self, _("environment component of rule %s has more than one phoneme placeholder ('_')"))
        if '#' in env and env.find('#') != 0 and \
               env.rfind('#') != len(env) - 1:
            raise InvalidRuleError(self, _("environment component of rule %s has text both before and after begin/end word marker ('#')"))
        if env.count('#') > 2:
            raise InvalidRuleError(self, _("environment component of rule %s has too many begin/end word markers ('#')"))

    def __check_asterisk_without_parenthesis (self, component):
        """Check that any asterisk character is preceded by a close
        parenthesis character."""
        if component.count('*') != component.count(')*'):
            raise InvalidRuleError(self, _("environment component of rule %s has repeater ('*') which does not follow parenthesised group"))
    
    def __check_mismatched_brackets (self, component):
        """Check that component does not have mismatched brackets.

        Check for invalid combinations of parentheses and square
        brackets. A square bracketted expression must not contain any
        parentheses."""
        openSB = False
        openP = False
        for char in component:
            if char == '(':
                if openSB:
                    raise InvalidRuleError(self, _("component of rule %s has parenthesis ('(') within square brackets ('[' and ']')"))
                if openP:
                    raise InvalidRuleError(self, _("component of rule %s has nested parentheses ('(' and ')')"))
                openP = True
            elif char == ')':
                if not openP:
                    raise InvalidRuleError(self, _("component of rule %s is missing an open parenthesis ('(')"))
                openP = False
            elif char == '[':
                if openSB:
                    raise InvalidRuleError(self, _("component of rule %s has nested square brackets ('[' and ']')"))
                openSB = True
            elif char == ']':
                if not openSB:
                    raise InvalidRuleError(self, _("component of rule %s is missing an open square bracket ('[')"))
                openSB = False
        if openSB:
            raise InvalidRuleError(self, _("component of rule %s is missing a close square bracket (']')"))
        if openP:
            raise InvalidRuleError(self, _("component of rule %s is missing a close parenthesis (')')"))

    def get_component (self, component, form):
        """Return value of component in form."""
        if not self.__components.has_key(form):
            if form == 'work':
                self.__components[form] = self.__original_components
        return self.__components[form][component]

    def __divide_rule (self, rule):
        """Split rule into source phoneme, target phoneme and
        environment and return list of components."""
        divider = self._get_divider()
        components = rule.split(divider)
        if len(components) != 3:
            raise InvalidRuleError(self, _('rule %s has the wrong number of components (must have three)'))
        return {'source': components[0], 'result': components[1],
                'environment': components[2]}

    def _get_divider (self):
        """Return the string used to divide rule components."""
        return '/'

    def get_reg_exp (self, variables={}):
        """Return regular expression pattern derived from environment
        and source phoneme.

        Every pattern consists of two named sections followed by a
        lookahead assertion. Using the lookahead assertion for the
        part of the pattern following the source phoneme seems
        necessary for multiple matches on the same string. A
        lookbehind assertion cannot be used in place of the named
        <start> section, because such an assertion must be fixed
        length, which is not necessarily the case here.
        
        """
        if self.__regexp:
            return self.__regexp
        env = self.get_component('environment', 'work')
        source = self.get_component('source', 'work')
        source = self.__replace_variables(source, variables)
        source = self.__escape_rule_part(source, ('\\', '$', '.', '^', '*',
                                                  '+', '?', '{', "'"))
        env = self.__escape_rule_part(env, ('.',))
        pattern = []
        pos = 0 # index of current character in string
        prev_char = '' # previous character in env
        for char in env:
            if (pos == 0 and char != '#') or (pos == 1 and prev_char == '#'):
                pattern.append('(?P<start>')
            if char == '_':
                pattern.append(')(?P<match>' + source + ')(?=')
            elif char == '#':
                if pos == 0:
                    pattern = ['^']
                else:
                    pattern.append(r'$)')
            elif char == ')':
                pattern.append(')?')
            elif char == '*':
                # Remove the previous character, because it must be a
                # ')?' derived from the parenthetical expression
                # preceding the asterisk, as verified elsewhere.
                pattern = pattern[:-1]
                pattern.append(')*')
            elif variables.has_key(char):
                pattern.append('[' + variables[char] + ']')
            else:
                pattern.append(char)
            if pos == len(env)-1 and char != '#':
                pattern.append(')')
            prev_char = char
            pos = pos + 1
        pattern_string = ''.join(pattern)
        try:
            self.__regexp = re.compile(pattern_string)
        except:
            raise InvalidRuleError(self, _('rule %s is malformed'))
        return self.__regexp

    def __replace_variables (self, string, variables):
        """Return string with all variables replaced by their values.

        Arguments:
        string -- string to replace variables in
        variables -- dictionary of variables
        
        """
        new_string = []
        if variables:
            for char in string:
                if variables.has_key(char):
                    new_string.append('[' + variables[char] + ']')
                else:
                    new_string.append(char)
            return ''.join(new_string)
        else:
            return string


    def __escape_rule_part (self, rule_part, escape_chars):
        """Return rule_part with all instances of escape_chars escaped
        for a regular expression.

        Arguments:
        rule_part -- string to be escaped
        escape_chars -- list of characters which must be escaped
        """
        for char in escape_chars:
            rule_part = rule_part.replace(char, r'\%s' % char)
        return rule_part

    def __eq__ (self, rule):
        return self.get_unformatted() == rule.get_unformatted()

    def __ne__ (self, rule):
        return self.get_unformatted() != rule.get_unformatted()


class Word:
    """Class for handling a lexicon item."""

    def __init__ (self, word):
        self.__original = word
        self.__form = {}
        self.__derivative = {}
        # __source is a reference to the Word object which was the
        # source word in the transformation which created this word.
        self.__source = None
        # __final_derivatives is a list of Word objects which are the
        # outcome of applying an entire set of rules to the word. This
        # is to save having to traverse the intervening Word objects
        # via the __derivatives attribute.
        self.__final_derivatives = []

    def set_derivative (self, rule, word):
        """Set the immediate derivative of self (rule and word
        that resulted from the application of that rule).

        Arguments:
        rule -- Rule object
        word -- Word object

        """
        self.__derivative['rule'] = rule
        self.__derivative['word'] = word

    def get_derivative (self):
        """Return a dictionary giving the immediate derivative of self."""
        return self.__derivative

    def add_final_derivative (self, word):
        """Add a final derivative word of self.

        Arguments:
        word -- Word object

        """
        self.__final_derivatives.append(word)

    def get_final_derivatives (self):
        """Return the final derivatives list of word objects."""
        return self.__final_derivatives

    def clear_derivatives (self):
        """Unset the immediate and final derivatives of self."""
        self.__derivative = {}
        self.__final_derivatives = []

    def gs_source (self, source=None):
        """Return the source Word of self, first setting it to source
        if source is present."""
        if source:
            self.__source = source
        return self.__source

    def get_form (self, form):
        """Return the specified form of self."""
        if not self.__form.has_key(form):
            # Derive and set the form.
            if form == 'display':
                self.__form[form] = self.__original
            elif form == 'work':
                self.__form[form] = self.__original
            else:
                raise InvalidWordFormError(self.get_form['display'], form,
                                           _('word %s has no %s form'))
        return self.__form[form]

    def __eq__ (self, word):
        return self.get_form('work') == word.get_form('work')

    def __ne__ (self, word):
        return self.get_form('work') != word.get_form('work')


class RulesParser:

    """Class for parsing the contents of a rules file."""

    def __init__ (self, lines, rule_class=Rule):
        self._dialects = {}
        self._groups = {}
        self._persistent = []
        self._phonotactics = {initial_syllable: [], medial_syllable: [],
                              final_syllable: []}
        self._rules = []
        self._variables = {}
        self._section_lines = {}
        self._dates = []
        self._Rule = rule_class
        self._parse_lines(lines)

    def _parse_lines (self, lines):
        """Parse lines into rules and sections."""
        # Prepare each line for processing as part of a specific
        # section.
        sections = {'Dialects': [], 'Groups': [], 'Persistent': [],
                    'Phonotactics': [], 'Rules': []}
        section = 'Rules'
        line_number = 0
        for line in lines:
            line_number = line_number + 1
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            if line.startswith('Section '):
                key = line[8:]
                if key in sections.keys():
                    section = key
                else:
                    message = _('Invalid section name %s in rules file at line %s')
                    raise InvalidSectionError(message, key, line_number)
                if sections['Rules']:
                    message = _('Invalid content outside section before line %s')
                    raise InvalidRulesFileError(message, line_number)
            else:
                sections[section].append(line)
        # Parse the contents of each section.
        self._parse_dialect_section(sections['Dialects'])
        self._parse_groups_section(sections['Groups'])
        self._parse_persistent_section(sections['Persistent'])
        self._parse_phonotactics_section(sections['Phonotactics'])
        self._parse_rules_section(sections['Rules'])

    def _parse_dialect_section (self, lines):
        """Parse the dialect section content in lines."""
        self._section_lines['Dialects'] = []
        for line in lines:
            parts = line.split('=')
            if len(parts) > 2:
                message = _('Invalid dialect definition %s: equals sign ("=") may not occur in either the abbreviation or display name')
                raise InvalidRulesFileError(message, line)
            elif len(parts) < 2:
                message = _('Invalid dialect definition %s: missing equals sign ("=")')
                raise InvalidRulesFileError(message, line)
            abbreviation = parts[0].strip()
            name = parts[1].strip()
            self._section_lines['Dialects'].append(line)
            self._dialects[abbreviation] = name

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
                rule = self._Rule(line)
                self._section_lines['Groups'].append(rule)
                rule = None
                try:
                    # Only record the line, not the Rule object, because
                    # the rule may be used in many different contexts.
                    self._groups[group].append(line)
                except KeyError:
                    raise InvalidRulesFileError(_('Invalid content outside of rule group definition'))

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
                        self._persistent.append(self._Rule(rule))
                else:
                    rule = self._Rule(parts[0])
                    self._persistent.append(rule)
                    self._section_lines['Persistent'].append(rule)
            elif len(parts) == 2:
                dialects = self._parse_dialects(parts[1])
                if self._groups.has_key(parts[0]):
                    self._section_lines['Persistent'].append((parts[0],
                                                              dialects))
                    for group_rule in self._groups[parts[0]]:
                        self._persistent.append(self._Rule(group_rule, None,
                                                           dialects))
                else:
                    rule = self._Rule(parts[0], None, dialects)
                    self._persistent.append(rule)
                    self._section_lines['Persistent'].append((rule, dialects))
            else:
                message = _('Malformed line (%s) in persistent rule section: no spaces are allowed in the either the rule or dialect parts')
                raise InvalidRulesFileError(message, line)

    def _parse_phonotactics_section (self, lines):
        """Parse the phonotactics section content in lines."""
        self._section_lines['Phonotactics'] = []
        for line in lines:
            parts = line.split('=')
            if len(parts) != 2:
                message = _('Invalid variable reference %s: format is variable name, equals sign ("="), variable definition')
                raise InvalidRulesFileError(message, line)
            name = parts[0].strip()
            definition = parts[1].strip()
            if name not in (initial_syllable, medial_syllable, final_syllable):
                message = _('Invalid phonotactic variable name %s: must be one of %s, %s or %s')
                raise InvalidRulesFileError(message, name, initial_syllable,
                                            medial_syllable, final_syllable)
            self._phonotactics[name].append(definition)
            self._section_lines['Phonotactics'].append(line)

    def _parse_rules_section (self, lines):
        """Parse the rules section content in lines."""
        self._section_lines['Rules'] = []
        if not lines:
            message = _('At least one rule must be specified in the rules section')
            raise InvalidRulesFileError(message)
        date = None
        for line in lines:
            parts = line.split('=')
            if len(parts) == 2:
                # Variable reference.
                var_name = parts[0].strip()
                var_data = parts[1].strip()
                self._variables[var_name] = var_data
                self._section_lines['Rules'].append(line)
            elif len(parts) > 2:
                # Invalid construction.
                message = _('Invalid variable reference %s: equals sign ("=") may not occur in either variable name or definition')
                raise InvalidRulesFileError(message, line)
            else:
                parts = line.split(' ')
                if len(parts) == 1:
                    try:
                        new_date = int(line)
                    except ValueError:
                        if self._groups.has_key(line):
                            self._section_lines['Rules'].append(line)
                            group = []
                            for rule in self._groups[parts[0]]:
                                group.append(self._Rule(rule, date))
                            self._rules.append(group)
                        else:
                            rule = self._Rule(parts[0], date)
                            self._rules.append(rule)
                            self._section_lines['Rules'].append(rule)
                    else:
                        if date is not None and new_date <= date:
                            message = _('Date %s is not later than the previously specified date')
                            raise InvalidRulesFileError(message, line)
                        else:
                            date = new_date
                            self._section_lines['Rules'].append(date)
                            self._dates.append(date)
                elif len(parts) == 2:
                    dialects = self._parse_dialects(parts[1])
                    if self._groups.has_key(parts[0]):
                        self._section_lines['Rules'].append((parts[0],
                                                             dialects))
                        group = []
                        for rule in self._groups[parts[0]]:
                            group.append(self._Rule(rule, date, dialects))
                        self._rules.append(group)
                    else:
                        rule = self._Rule(parts[0], date, dialects)
                        self._rules.append(rule)
                        self._section_lines['Rules'].append((rule, dialects))
                else:
                    message = _('Malformed line (%s) in rule section: no spaces are allowed in either the rule or dialect parts')
                    raise InvalidRulesFileError(message, line)

    def _parse_dialects (self, dialects):
        """Return a tuple of dialect abbreviations from dialects.

        Arguments:
        dialects -- string of dialect abbreviations, separated by commas

        """
        dialect_list = dialects.split(',')
        # Check that each dialect has been defined.
        for dialect in dialect_list:
            if not self._dialects.has_key(dialect):
                message = _('Unrecognised dialect abbreviation %s')
                raise InvalidRulesFileError(message, dialect)
        return dialect_list

    def get_rules (self, start_date=None, end_date=None, dialect=None):
        """Return a list of rules which match the provided criteria.

        Arguments:
        start_date -- integer of date after which rules must occur
        end_date -- integer of date before which rules must occur
        dialect -- string of dialect to which rules must apply

        """
        persistent_rules = []
        if start_date > end_date:
            raise InvalidRulesSetError(_('Start date must be earlier than end date for transformation'))
        if dialect and dialect not in self._dialects.keys():
            raise InvalidRulesSetError(_('Dialect must be one of those defined in the ruleset for transformation'))
        for rule in self._persistent:
            dialects = rule.get_dialects()
            if dialect not in dialects and dialects:
                continue
            persistent_rules.append(rule)
        rules = []
        for rule in self._rules:
            if type(rule) == type([]):
                if self._check_rule(rule[0], start_date, end_date, dialect):
                    rules.extend(rule)
                    rules.extend(persistent_rules)
            else:
                if self._check_rule(rule, start_date, end_date, dialect):
                    rules.append(rule)
                    rules.extend(persistent_rules)
        return rules

    def _check_rule (self, rule, start_date, end_date, dialect):
        """Return True if rule matches the provided criteria."""
        date = rule.get_date()
        if start_date and (start_date > date or date is None):
            return False
        if end_date and (end_date < date or date is None):
            return False
        dialects = rule.get_dialects()
        if dialect not in dialects and dialects:
            return False
        return True

    def get_variables (self):
        """Return dictionary of variables."""
        return self._variables

    def get_phonotactics (self):
        """Return dictionary of phonotactic variables."""
        return self._phonotactics

    def get_lines (self):
        """Return dictionary of meaningful section lines."""
        return self._section_lines

    def get_dialects (self):
        """Return dictionary of dialect abbreviations and names."""
        return self._dialects

    def get_dates (self):
        """Return list of dates in ascending order."""
        return self._dates
    

def compile_words (lexicon):
    """Return list of word objects created from list of word strings."""
    words = []
    for item in lexicon:
        item = item.strip()
        if not item:
            continue
        words.append(Word(item))
    return words
