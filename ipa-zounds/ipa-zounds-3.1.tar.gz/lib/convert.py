# IPA Zounds, a sound change engine with support for the IPA.
# Copyright (C) 2005 Jamie Norrish
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

"""This module contains classes for converting between IPA Unicode
characters and other scripts."""

import codecs
import ConfigParser
import gettext
import os.path

from ipazounds import locale_dir, ipadata, xsampadata

t = gettext.translation('ipazounds', locale_dir, fallback=True)
_ = t.ugettext

NFPM = 'Y' # Constant for normal form phoneme marker
homorganic_variables = ipadata.homorganic_variables


class ConvertError (Exception):
    """Base exception class for conversion errors."""
    def __init__ (self, problem, input_string):
        Exception.__init__(self)
        self.problem = problem.encode('utf-8')
        self.input_string = input_string.encode('utf-8')

    def __unicode__ (self):
        return self.__str__().decode('utf-8')

class MappingError (ConvertError):
    """Exception class for missing/invalid script files."""
    def __init__ (self, problem):
        self.problem = problem.encode('utf-8')

    def __str__ (self):
        return self.problem

class InvalidFeatureError (ConvertError):
    """Exception class for invalid/malformed features."""
    def __init__ (self, input_string, feature, problem):
        ConvertError.__init__(self, problem, input_string)
        self.feature = feature.encode('utf-8')

    def __str__ (self):
        return self.problem % (self.feature, self.input_string)

class NoDelimiterError (ConvertError):
    """Exception class for missing delimiters in binary feature and
    suprasegmental feature sets."""
    def __init__ (self, input_string, problem):
        ConvertError.__init__(self, problem, input_string)

    def __str__ (self):
        return self.problem % self.input_string
    
class NoFeatureSignError (ConvertError):
    """Exception class for features lacking a sign (+ or -)."""
    def __init__ (self, input_string, feature, problem):
        ConvertError.__init__(self, problem, input_string)
        self.feature = feature.encode('utf-8')

    def __str__ (self):
        return self.problem % (self.feature, self.input_string)

class InvalidCharError (ConvertError):
    """Exception class for invalid script input."""
    def __init__ (self, input_string, character, script, problem):
        ConvertError.__init__(self, problem, input_string)
        self.character = character.encode('utf-8')
        self.script = script.encode('utf-8')

    def __str__ (self):
        return self.problem % (self.character, self.input_string, self.script)


def sort_keys (a, b):
    """Sort function for the keys of a transliteration mapping
    dictionary. The sort is done by length."""
    return cmp(len(b), len(a))


class Converter:
    """Delegating class for handling transliteration to and from IPA
    and another script."""

    def __init__ (self):
        self.__converters = {}
        self.__data_path = ''

    def __get_converter (self, script_name):
        """Return the conversion object for script_name, creating one
        if it isn't defined."""
        if not self.__converters.has_key(script_name):
            if script_name == 'normalised':
                self.__converters[script_name] = NormalisedFormConverter()
            elif script_name == 'xsampa':
                self.__converters[script_name] = XSAMPAConverter()
            else:
                self.__converters[script_name] = GenericConverter(script_name,
                                                                  self.__data_path)
        return self.__converters[script_name]

    def __clear_converters (self):
        """Clear the list of known converters."""
        # Don't remove the normalised form converter.
        for key in self.__converters.keys():
            if key == 'normalised':
                continue
            del self.__converters[key]

    def set_data_path (self, path):
        """Set the path to the directory containing user-defined
        mappings."""
        if path != self.__data_path:
            self.__clear_converters()
            self.__data_path = path

    def get_data_path (self):
        """Return the path to the directory containing user-defined
        mappings."""
        return self.__data_path

    def script_to_ipa (self, script, script_name):
        """Return script in script_name converted to IPA characters."""
        converter = self.__get_converter(script_name)
        return converter.script_to_ipa(script)

    def ipa_to_script (self, ipa, script_name):
        """Return ipa converted to script_name characters."""
        converter = self.__get_converter(script_name)
        return converter.ipa_to_script(ipa)

    def get_rule_divider (self, script_name):
        """Return the string used to divide rule components in
        script_name."""
        converter = self.__get_converter(script_name)
        return converter.get_rule_divider()

    def get_bf_set_markers (self, script_name):
        """Return a list of the strings used to mark off sets of
        binary features (opening marker, closing marker)."""
        converter = self.__get_converter(script_name)
        return converter.get_bf_set_markers()
    

class GenericConverter:
    """Class for handling user-defined transliterations to and from IPA."""

    def __init__ (self, script_name, data_path):
        self.script_name = script_name
        # Load the mapping data for script_name.
        self.to_ipa_map = {}
        self.to_script_map = {}
        self.ipa_keys = []
        self.script_keys = []
        self.open_brackets = {'ssf': '', 'bf': ''}
        self.close_brackets = {'ssf': '', 'bf': ''}
        self.rule_divider = ''
        self.__parse_mapping(data_path)
        self._set_keys()

    def __parse_mapping (self, data_path):
        """Return the mapping information for script from the
        file in data_path."""
        filename = '%s.orth' % os.path.join(data_path, self.script_name)
        try:
            file_handle = codecs.open(filename, 'rU', 'utf-8')
        except IOError, err:
            message = 'Unable to use script file %s: %s' % (filename, err)
            raise MappingError(message)
        config = ConfigParser.ConfigParser()
        try:
            config.readfp(file_handle)
        except ConfigParser.Error, err:
            file_handle.close()
            raise MappingError('In script file %s: %s' % (filename, err))
        file_handle.close()
        for section in ('Script to IPA', 'IPA to Script', 'Rule Characters'):
            if not config.has_section(section):
                message = 'Script file %s is missing the %s section' \
                          % (filename, section)
                raise MappingError(message)
            if section == 'Script to IPA':
                for option in config.options(section):
                    if option == 'hash':
                        key = '#'
                    elif option == 'colon':
                        key = ':'
                    elif option == 'equals':
                        key = '='
                    else:
                        key = option
                    self.to_ipa_map[key] = config.get(section, option)
            elif section == 'IPA to Script':
                for option in config.options(section):
                    self.to_script_map[option] = config.get(section, option)
            elif section == 'Rule Characters':
                # Some characters defined in this section belong
                # internally to the mapping.
                rule_chars = ('hash', '_', '(', ')', '*')
                map_additions = []
                try:
                    self.open_brackets['ssf'] = config.get(section, 'ssf_open')
                    self.open_brackets['bf'] = config.get(section, 'bf_open')
                    self.close_brackets['ssf'] = config.get(section,
                                                            'ssf_close')
                    self.close_brackets['bf'] = config.get(section, 'bf_close')
                    self.rule_divider = config.get(section, 'rule_divider')
                    for char in rule_chars:
                        map_additions.append((char, config.get(section, char)))
                except ConfigParser.Error, err:
                    raise MappingError('In script file %s: %s' % (filename,
                                                                  err))
                # Add the mapping characters to the maps.
                for ipa_char, script_char in map_additions:
                    # The configuration file treats a line-beginning
                    # '#' as a comment marker, so it must be
                    # 'escaped'. Unescape it here.
                    if ipa_char == 'hash':
                        ipa_char = '#'
                    self.to_ipa_map[script_char] = ipa_char
                    self.to_script_map[ipa_char] = script_char

    def _set_keys (self):
        """Set variables for holding length-sorted keys for the
        mapping dictionaries."""
        self.ipa_keys = self.to_script_map.keys()
        self.ipa_keys.sort(sort_keys)
        self.script_keys = self.to_ipa_map.keys()
        self.script_keys.sort(sort_keys)

    def __convert_script (self, script, is_ipa):
        """Return script converted either to or from IPA depending on
        whether script is in IPA or not."""
        # Iterate through the keys of the mapping, checking for a
        # match at the start of the string. If found, add the mapped
        # equivalent to the output, remove the matched characters from
        # the string, and restart the process.
        #
        # The only exceptions are bracketted characters (within <> and
        # []), which are, with their brackets, copied across unchanged.
        original = script
        if is_ipa:
            mapping = self.to_script_map
            keys = self.ipa_keys
            open_brackets = ['<', '[']
            close_brackets = ['>', ']']
            error_message = _('Character %s in %s cannot be converted to script %s')
        else:
            mapping = self.to_ipa_map
            keys = self.script_keys
            open_brackets = self.open_brackets.values()
            close_brackets = self.close_brackets.values()
            error_message = _('Character %s in %s cannot be converted from script %s')
        output = []
        bracketted = False
        while script:
            if bracketted:
                output.append(script[0])
                if script[0] in close_brackets:
                    bracketted = False
                script = script[1:]
                continue
            for key in keys:
                if script.startswith(key):
                    output.append(mapping[key])
                    script = script[len(key):]
                    break
            else:
                if script[0] in open_brackets:
                    bracketted = True
                    output.append(script[0])
                    script = script[1:]
                else:
                    raise InvalidCharError(original, script[0],
                                           self.script_name, error_message)
        return ''.join(output)

    def script_to_ipa (self, script):
        """Return script string converted to IPA characters."""
        return self.__convert_script(script, False)

    def ipa_to_script (self, ipa):
        """Return ipa string converted to script characters."""
        return self.__convert_script(ipa, True)

    def get_rule_divider (self):
        """Return the string used to divide rule components."""
        return self.rule_divider

    def get_bf_set_markers (self):
        """Return a list of the strings used to mark off sets of
        binary features (opening marker, closing marker)."""
        return (self.open_brackets['bf'], self.close_brackets['bf'])


class NormalisedFormConverter (GenericConverter):
    """Class for handling conversion between IPA and normalised form
    (IPA Zounds' internal representation)."""

    ipa_map = ipadata.ipa_map
    ipa_base_chars = ipadata.ipa_base_chars
    ipa_space_chars = ipadata.ipa_space_chars
    ipa_diacritics = ipadata.ipa_diacritics
    ipa_supra_segmentals = ipadata.ipa_supra_segmentals
    ipa_ss_map = ipadata.ipa_ss_map
    features = ipa_map.keys()
    features.sort()
    number_features = len(features)
    # Construct a base feature set for a sound
    base_feature_set = ['2' for f in features]
    base_feature_set.insert(0, NFPM)
    feature_values = homorganic_variables.values()
    feature_values.extend(['0', '1'])
    markers = homorganic_variables.keys()
    markers.extend(['+', '-', u'\N{MINUS SIGN}'])
    # These are not meant to used, but are useful for completeness and
    # debuggin rule display purposes.
    rule_divider = '/'
    open_brackets = {'ssf': '', 'bf': '{'}
    close_brackets = {'ssf': '', 'bf': '}'}

    # Normalised form represents each phoneme with a string which
    # begins with the NFPM (normal form phoneme marker) and is
    # followed by as many digits as there are binary features in
    # the model used. Only the digits 0, 1 and 2 are used. 0 means
    # that the feature is not present, 1 means that the feature is
    # present, and 2 means that the feature may or may not be
    # present. Each normal form string is joined to the previous
    # one (in order of the phonemes).
    #
    # Suprasegmentals are represented as IPA
    # characters. Suprasegmental features are converted to a
    # character class consisting of the matching IPA characters.

    def __init__ (self):
        # The next two dictionaries cache mappings to and from IPA
        # characters and normal forms, for performance improvements.
        self.__map_to_ipa = {}
        self.__map_to_nf = {}
        self.__input = ''

    def __bf_to_normalised (self, bf):
        """Return string or list of strings of binary features
        converted to normalised form."""
        normal_form = []
        feature = ''
        is_feature = 0
        feature_value = '2'
        for char in bf:
            if char == '[':
                normal_form.append(self.base_feature_set[:])
                is_feature = 1
            elif char == ']':
                is_feature = 0
                if feature:
                    try:
                        index = self.features.index(feature) + 1
                    except ValueError:
                        raise InvalidFeatureError(self.__input, feature,
                                                  _('%s is not a valid binary feature in %s'))
                    if feature_value not in self.feature_values:
                        raise NoFeatureSignError(self.__input, feature,
                                                 _('Binary feature %s in %s has no sign (+ or -)'))
                    normal_form[-1][index] = feature_value
                    feature = ''
            elif is_feature:
                if char in self.markers:
                    if feature:
                        try:
                            index = self.features.index(feature) + 1
                        except ValueError:
                            raise InvalidFeatureError(self.__input, feature,
                                                      _('%s is not a valid binary feature in %s'))
                        normal_form[-1][index] = feature_value
                        feature = ''
                    if char == '+':
                        feature_value = '1'
                    elif char in ('-', u'\N{MINUS SIGN}'):
                        feature_value = '0'
                    else:
                        feature_value = self.feature_values[self.markers.index(char)]
                else:
                    feature = feature + char
            else:
                normal_form.append([char])
        normal_form = [''.join(part) for part in normal_form]
        return ''.join(normal_form)

    def __ssf_to_normalised (self, ssf):
        """Convert string of suprasegmental feature to normalised
        form.

        It is assumed that there is a single feature in SSF, preceded
        by a + or - sign and optionally surrounded by parentheses.
        """
        # SSF may be an empty string, in which case a generic
        # suprasegmental is desired
        if not ssf:
            normal_form = '[' + ''.join(self.ipa_supra_segmentals) + ']'
            return normal_form
        if ssf[0] not in ('+', '-', u'\N{MINUS SIGN}'):
            raise NoFeatureSignError(self.__input, ssf,
                                     _('Suprasegmental feature %s has no sign (+ or -) in %s'))
        if ssf[0] == '+':
            sign = 'plus'
        else:
            sign = 'minus'
        try:
            chars = self.ipa_ss_map[ssf[1:]][sign]
        except KeyError:
            raise InvalidFeatureError(self.__input, ssf,
                                      _('%s is not a valid suprasegmental feature in %s'))
        if chars:
            normal_form = '[' + ''.join(chars) + ']'
        else:
            normal_form = ''
        return normal_form

    def __ipa_to_normalised (self, ipa):
        """Convert string or list of strings of IPA characters to
        normalised form.

        This method is for strings which consist solely of IPA characters.

        Arguments:
        ipa -- string or list of single character strings

        """
        normal_form = []
        segment = ''
        if type(ipa) != type(''):
            ipa = ''.join(ipa)
        # Use lookup table if we've handled this set of characters
        # before.
        if self.__map_to_nf.has_key(ipa):
            return self.__map_to_nf[ipa]
        for codepoint in ipa:
            if codepoint in self.ipa_supra_segmentals:
                normal_form.append(segment + codepoint)
                segment = ''
                continue
            elif codepoint in self.ipa_base_chars:
                normal_form.append(segment)
                # Use lookup table if we've handled this character before.
                if self.__map_to_nf.has_key(codepoint):
                    segment = self.__map_to_nf[codepoint]
                    continue
                # Start all features out as either.
                segment = ''.join(self.base_feature_set)
            elif codepoint in self.ipa_diacritics or \
                     codepoint in self.ipa_space_chars:
                # Check that there has been an IPA base character
                # prior to this character.
                if not segment:
                    raise InvalidCharError(self.__input, codepoint, 'IPA',
                                           _('%s in %s does not follow an %s base character'))
            else:
                # Invalid character.
                raise InvalidCharError(self.__input, codepoint, 'IPA',
                                       _('%s in %s is not a recognised %s character'))
            # Set the feature values for the character.
            feature_number = 1
            for feature in self.features:
                if codepoint in self.ipa_map[feature]['plus']:
                    segment = segment[0:feature_number] + '1' \
                              + segment[feature_number+1:]
                elif codepoint in self.ipa_map[feature]['minus']:
                    segment = segment[0:feature_number] + '0' \
                              + segment[feature_number+1:]
                feature_number = feature_number + 1
            # Create lookup table entry for character.
            if codepoint in self.ipa_base_chars:
                self.__map_to_nf[codepoint] = segment
                self.__map_to_ipa[segment] = codepoint
        normal_form = ''.join(normal_form) + segment
        # Create lookup table entry for entire string.
        self.__map_to_nf[ipa] = normal_form
        return normal_form

    def ipa_to_script (self, ipa):
        """Convert IPA string to normalised form.

        This method takes into account non-IPA characters which are
        valid within a rule.

        """
        self.__input = ipa
        normal_form = []
        group = []
        index = 0
        while index < len(ipa):
            char = ipa[index]
            if char == u'\N{EMPTY SET}':
                group = []
                normal_form = []
                break
            # Don't convert rule-significant characters (which are
            # not IPA symbols)
            if char in ('_', '#', '(', ')', '*'):
                if group:
                    normal_form.append(self.__ipa_to_normalised(group))
                    group = []
                normal_form.append(char)
            elif char == '[':
                if group:
                    normal_form.append(self.__ipa_to_normalised(group))
                    group = []
                remainder = ipa[index:]
                try:
                    rsb_index = remainder.index(']')
                except ValueError:
                    message = _(u'Missing right square bracket in %s')
                    raise NoDelimiterError(self.__input, message)
                bf_string = remainder[:rsb_index+1]
                normal_form.append(self.__bf_to_normalised(bf_string))
                index = index + rsb_index
            elif char == '<':
                if group:
                    normal_form.append(self.__ipa_to_normalised(group))
                    group = []
                remainder = ipa[index:]
                try:
                    rab_index = remainder.index('>')
                except ValueError:
                    message = _(u'Missing right angle bracket in %s')
                    raise NoDelimiterError(self.__input, message)
                ssf_string = remainder[1:rab_index]
                normal_form.append(self.__ssf_to_normalised(ssf_string))
                index = index + rab_index
            else:
                group.append(char)
            index = index + 1
        if group:
            # Must be unconverted IPA characters.
            normal_form.append(self.__ipa_to_normalised(group))
        return ''.join(normal_form).replace('2', '[01]')
                    
    def script_to_ipa (self, normal_form):
        """Convert normalised form string to IPA characters."""
        ipa = []
        segments = normal_form.split(NFPM)
        # Ignore the first string generated by the split if it is
        # empty (suprasegmentals may occur there).
        if not segments[0]:
            segments = segments[1:]
        for segment in segments:
            # Use lookup table if we've handled this segment before.
            if self.__map_to_ipa.has_key(segment[:self.number_features]):
                ipa.append(self.__map_to_ipa[segment[:self.number_features]])
                ipa.append(segment[self.number_features:])
                continue
            # Just add the segment if it consists solely of a
            # suprasegmental.
            if segment in self.ipa_supra_segmentals:
                ipa.append(segment)
                continue
            # Get the IPA character from that part of the segment
            # which represents a character. Anything left over should
            # be a suprasegmental.
            ipa_char = self.__segment_to_ipa(segment[:len(self.ipa_map)])
            # Add mapping to lookup table
            self.__map_to_ipa[segment[:len(self.ipa_map)]] = ipa_char
            # Add the IPA character plus any suprasegmentals.
            ipa.append(ipa_char + segment[len(self.ipa_map):])
        return ''.join(ipa)

    def __segment_to_ipa (self, segment):
        """Return the IPA character matching segment of normalised
        form."""
        segment_index = 0
        segment_feature_values = {}
        # Create list of characters possessing any of segment's
        # features. Also keep track of whether each feature is
        # plus or minus for this segment.
        counter = Counter()
        for feature_value in segment:
            if feature_value == '1':
                sign = 'plus'
            else:
                sign = 'minus'
            # Create a list of characters with their frequency
            for char in self.ipa_map[self.features[segment_index]][sign]:
                counter.add(char)
            segment_feature_values[self.features[segment_index]] = sign
            segment_index = segment_index + 1
        char_frequency = counter.counts()
        # Try the character which matches the most features first.
        char = char_frequency[0][1]
        if char_frequency[0][0] == len(self.features):
            # We have an exact match using the base character.
            ipa_char = char
        else:
            # Get a set of modifiers/diacritics to make up the
            # required feature set.
            missing = []
            diacritics = []
            mods = []
            for i in range(self.number_features+1):
                try:
                    diacritics, mods = self.__find_modifiers(char, segment_feature_values)
                    break
                except IndexError:
                    # There are no modifiers which can make up the
                    # required feature set, so try the character
                    # which matches the next most features.
                    char = char_frequency[i][1]
            if not diacritics and not mods:
                # We haven't found any characters + diacritics
                # which match, so use the best character and add
                # the missing features with feature notation.
                char = char_frequency[0][1]
                for feature in self.features:
                    if char not in self.ipa_map[feature][segment_feature_values[feature]]:
                        if segment_feature_values[feature] == 'plus':
                            sign = '+'
                        else:
                            sign = '-'
                        missing.append('[%s%s]' % (sign, feature))
            ipa_char = char + ''.join(diacritics) + ''.join(mods) \
                       + ''.join(missing)
        return ipa_char

    def __find_modifiers (self, base_char, segment_feature_values):
        """Return diacritical marks and spacing modifiers to achieve
        the features for a segment not covered by the base character.

        Arguments:
        base_char -- string of base character
        segment_feature_values -- dictionary of features and their
                                  values for the segment
        
        """
        diacritics = []
        mods = []
        # Create lists of features matched by the base character and
        # those which aren't.
        null_chars = []
        mark_chars = []
        null_features = []
        mark_features = []
        # Keep a record of which features are accounted for by the
        # base IPA character, and which we need to find a modifier to
        # handle.
        for feature in self.features:
            # Check whether that base character already accounts for
            # this feature value.
            if base_char in self.ipa_map[feature][segment_feature_values[feature]]:
                # We don't want to use *any* characters which relate
                # to this feature.
                null_features.append(feature)
                null_chars.extend(self.ipa_map[feature]['plus'])
                null_chars.extend(self.ipa_map[feature]['minus'])
            else:
                mark_features.append(feature)
                mark_chars.extend(self.ipa_map[feature][segment_feature_values[feature]])
        while mark_features:
            # Get list of characters with their frequency
            counter = Counter()
            for char in mark_chars:
                # Remove characters that are associated with already
                # matched features from the list of possible
                # characters.
                if char not in null_chars:
                    counter.add(char)
            char_frequency = counter.counts()
            # Always use the character that matches the most features.
            # If there is no character, then the base character is
            # incorrect; an IndexError exception is raised and a new
            # base character is picked.
            char = char_frequency[0][1]
            if char in self.ipa_space_chars:
                mods.append(char)
            else:
                diacritics.append(char)
            mark_features = [feature for feature in mark_features if char not in self.ipa_map[feature][segment_feature_values[feature]]]
            null_chars.extend(char)
        mods.sort(self.__sort_mods)
        return (diacritics, mods)

    def __sort_mods (self, a, b):
        """Sort IPA modifying characters, since they should occur
        in a certain order.

        Arguments:
        a -- first character being compared
        b -- second character being compared. This is not used, but the
             inbuilt sort method passes it.

        """
        # The only requirement we have is that the length marker come
        # last.
        if a == u'\N{MODIFIER LETTER TRIANGULAR COLON}':
            return 1
        else:
            return -1


class Counter:
    """Class for determining the frequency of members in a list."""

    def __init__ (self):
        self.dict = {}

    def add (self, item):
        """Add an item to the list."""
        self.dict[item] = self.dict.get(item, 0) + 1

    def counts (self):
        """Returns list of keys, sorted by descending values."""
        result = [[val, key] for (key, val) in self.dict.items()]
        result.sort()
        result.reverse()
        return result


class XSAMPAConverter (GenericConverter):
    """Class for handling conversion between X-SAMPA and Unicode IPA."""

    def __init__ (self):
        self.script_name = 'X-SAMPA'
        self.to_ipa_map = xsampadata.xsampa_map
        self.to_script_map = xsampadata.ipa_map
        self._set_keys()
        self.open_brackets = xsampadata.open_brackets
        self.close_brackets = xsampadata.close_brackets
        self.rule_divider = xsampadata.rule_divider
