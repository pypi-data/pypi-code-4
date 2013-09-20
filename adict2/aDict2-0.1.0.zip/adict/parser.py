# aDict — simple dictionary handling
#
# Authors:
#     arseniiv <arseniiv@gmail.com>
#
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

"""parser.py — aDict parser
"""

__all__ = [
    "DictionaryParseError",
    "Parser"
    ]

import io
import re

from adict._data import *
from adict._data import (FORMAT_NONE, FORMAT_SW, FORMAT_EM, FORMAT_REM)
from adict._strings import *


class DictionaryParseError(Exception):
    
    def __init__(self, lineno, expected_lines, source):
        self.lineno = lineno
        self.line_types = expected_lines
        self.source = source
    
    def __str__(self):
        return "line types {expected_lines} expected on line {lineno} in {source!r}".format(**self)

class Parser:
    """Parser of aDict-formatted strings and files.
    
    Usage:
    
    p = Parser(str or TextIOBase)
    dictionary = p.Parse()
    """
    
    def __init__(self, source):
        """Create a parser from source.
        
        source is either a string or a text file
        """
        if isinstance(source, str):
            self.line_iter = iter(source.splitlines())
        elif isinstance(source, io.TextIOBase):
            self.line_iter = source
        else:
            raise TypeError('source must be either a string or a text file')
        self.line_iter = enumerate(self.line_iter)
        self.source = source
    
    def parse(self) -> Dictionary:
        """Parse specified source and produce a Dictionary."""
        self.parsed_dictionary = dictionary = Dictionary()
        state = State.pre_signature
        for lineno, line in self.line_iter:
            lineno += 1
            line = decomment_and_normalize(line)
            if line == "": continue
            parsed = False
            expected_lines = State.expected_lines(state)
            for t in expected_lines:
                parsed, state = t.parse_line(state, dictionary, line, lineno)
                if parsed: break
            if not parsed:
                raise DictionaryParseError(lineno, expected_lines, self.source)
        if State.is_not_final(state):
            raise DictionaryParseError(lineno + 1, expected_lines, self.source)
        try:
            del dictionary._last_article
            del dictionary._last_definition
            del dictionary._last_example
            del dictionary._last_idiom
        except AttributeError:
            pass
        return dictionary
        

def normalize(s):
    """Trims whitespace from string s."""
    return s.strip(inline_whitespace)

def decomment_and_normalize(s):
    """Trims whitespace and comments from string s."""
    index = s.find(inline_comment_start)
    if index != -1:
        s = s[0:index]
    return s.strip(inline_whitespace)

def parse_bracketed(s, left, right):
    """If s have form <left><text><right>, returns text normalized.
    Else, returns None.
    """
    if s.startswith(left) and s.endswith(right):
        return normalize(s[len(left) : -len(right)])
    else:
        return None

def parse_special_word(s):
    """If s has form '#'<sw>'#'<text>, returns (sw, text).
    Else, returns (None, text).
    """
    index1 = s.find(special_word_marker)
    if index1 != -1:
        index2 = s.find(special_word_marker, index1 + 1)
        if index2 != -1:
            sw = normalize(s[index1+len(special_word_marker) : index2])
            rest = normalize(s[index2+len(special_word_marker) :])
            return sw, rest
    return None, s

def make_title(s):
    """If s has form <text>'*'<num>, returns (text, num).
    Otherwise, returns text.
    """
    index = s.find(homonym_separator)
    if index != -1:
        text = normalize(s[0:index])
        num = normalize(s[index+len(homonym_separator) :])
        try:
            num = int(num)
        except ValueError:
            pass
        else:
            return text, num
    return normalize(s)

_format_re = re.compile(format_re)

def formatted(s):
    """If s contains substrings of form '#'<txt>'#', '(('<txt>'))',
    "''"<txt>"''", returns list of tuples (FORMAT_x, txt).
    Otherwise, returns s.
    """
    matches = re.findall(_format_re, normalize(s))
    if len(matches) == 1 and matches[0][0] != '':
        return matches[0][0]
    def to_fmt(txt_none, txt_sw, txt_rem, txt_em):
        if txt_none != '':
            return FORMAT_NONE, txt_none
        elif txt_sw != '':
            return FORMAT_SW, txt_sw
        elif txt_rem != '':
            return FORMAT_REM, txt_rem
        elif txt_em != '':
            return FORMAT_EM, txt_em
    return [to_fmt(*m) for m in matches]


class Line:
    """Type of source line."""
    
    def __new__(cls):
        return None

class SignatureLine(Line):
    """Format signature."""
    
    def parse_line(state, dictionary, line, lineno):
        value = parse_bracketed(line, *section_brackets)
        if value == None or value.lower() != signature_section_name:
            return False, state
        return True, State.pre_section

class PropertiesSectionLine(Line):
    """Properties section header."""
    
    def parse_line(state, dictionary, line, lineno):
        value = parse_bracketed(line, *section_brackets)
        if value == None or value.lower() != properties_section_name:
            return False, state
        dictionary.properties_lineno = lineno
        return True, State.in_properties

class ArticlesSectionLine(Line):
    """Articles section header."""
    
    def parse_line(state, dictionary, line, lineno):
        value = parse_bracketed(line, *section_brackets)
        if value == None or value.lower() != articles_section_name:
            return False, state
        dictionary.articles_lineno = lineno
        return True, State.in_articles

class NameValueLine(Line):
    """Name-value pair."""
    
    def parse_line(state, dictionary, line, lineno):
        i = line.find(name_value_separator)
        if i == -1:
            return False, state
        name = normalize(line[0:i])
        value = normalize(line[i+len(name_value_separator) :])
        dictionary.properties[name] = value
        return True, State.in_properties

class TitleLine(Line):
    """Article title."""
    
    def parse_line(state, dictionary, line, lineno):
        a = Article(make_title(line))
        a.lineno = lineno
        dictionary._last_article = a
        dictionary.articles.append(a)
        return True, State.in_article

class TitleLinkLine(Line):
    """Article content as link."""
    
    def parse_line(state, dictionary, line, lineno):
        if line.startswith(link_marker):
            t = make_title(line[len(link_marker) :])
            dictionary._last_article.content = LinkContent(t)
            return True, state
        elif line.startswith(form_link_marker):
            sw, text = parse_special_word(line[len(form_link_marker) :])
            t = make_title(text)
            dictionary._last_article.content = FormContent((sw, t))
            return True, state
        else:
            return False, state
        
class AttributeLine(Line):
    """Article attribute."""
    
    def parse_line(state, dictionary, line, lineno):
        text = parse_bracketed(line, *transcription_brackets)
        if text != None:
            dictionary._last_article.transcriptions.append(text)
            return True, state
        if line.startswith(special_word_marker):
            sw, text = parse_special_word(line)
            if sw != None:
                if text == "":
                    dictionary._last_article.classes.append(sw)
                else:
                    dictionary._last_article.forms.append((sw, text))
                return True, state
        if line.startswith(etymology_marker):
            text = line[len(etymology_marker) :]
            dictionary._last_article.etymologies.append(formatted(text))
            return True, state
        return False, state
    
class DefinitionLine(Line):
    """One of article title meanings."""
    
    def parse_line(state, dictionary, line, lineno):
        if line.startswith(meaning_marker):
            text = formatted(line[len(meaning_marker) :])
            d = Definition(text)
            dictionary._last_definition = d
            if dictionary._last_article.content == None:
                dictionary._last_article.content = []
            dictionary._last_article.content.append(d)
            return True, State.in_definition
        else:
            return False, state

class AdditionLine(Line):
    """Additional meaning attribute."""
    
    def parse_line(state, dictionary, line, lineno):
        if line.startswith(example_marker):
            text = formatted(line[len(example_marker) :])
            dictionary._last_example = text
            dictionary._last_idiom = None
            return True, State.in_example
        elif line.startswith(idiom_marker):
            text = formatted(line[len(idiom_marker) :])
            dictionary._last_example = None
            dictionary._last_idiom = text
            return True, State.in_idiom
        else:
            i = line.find(link_marker)
            if i != -1:
                f = line[0:i]
                if f == "": f = None
                t = make_title(line[i+len(link_marker) :])
                dictionary._last_definition.links.append((f, t))
                return True, state
        return False, state

class TranslationLine(Line):
    """Translation of an example or an idiom."""
    
    def parse_line(state, dictionary, line, lineno):
        if line.startswith(translation_marker):
            text = formatted(line[len(translation_marker) :])
            if dictionary._last_example != None:
                dictionary._last_definition.examples.append(
                    (dictionary._last_example, text))
            elif dictionary._last_idiom != None:
                dictionary._last_definition.idioms.append(
                    (dictionary._last_idiom, text))
            return True, State.in_definition
        return False, state

class State:
    """Parser state helper."""

    def __new__(cls):
        return None
    
    pre_signature = 0
    pre_section = 1
    in_properties = 2
    in_articles = 3
    in_article = 4
    in_definition = 5
    in_example = 6
    in_idiom = 7
    
    _not_final_states = (in_example, in_idiom, pre_signature)
    
    _expected_lines = {
        pre_signature: (SignatureLine,),
        pre_section: (PropertiesSectionLine, ArticlesSectionLine),
        in_properties: (NameValueLine, ArticlesSectionLine),
        in_articles: (TitleLine,),
        in_article: (AttributeLine, TitleLinkLine, DefinitionLine, TitleLine),
        in_definition: (AdditionLine, DefinitionLine, TitleLine),
        in_example: (TranslationLine,),
        in_idiom: (TranslationLine,)
        }
    
    @classmethod
    def is_not_final(cls, state):
        """Shows whether the state final or not."""
        return state in cls._not_final_states
    
    @classmethod
    def expected_lines(cls, state):
        """Returns a tuple of Line subclasses applicable on the state."""
        return cls._expected_lines[state]



