import sys
_PY3 = sys.version_info[0] >= 3
if _PY3:
    from html.entities import codepoint2name, name2codepoint
    unichr = chr
    unicode = str
else:
    from htmlentitydefs import codepoint2name, name2codepoint
import re
import codecs

NAMED_ENT   = unicode('&{0};')
NUMERIC_ENT = unicode('&#{0};')

__all__ = """named_entities numeric_entities hex_entities
             unicode_entities unescape encode_ampersands""".strip().split()


def unescape(text):
    """
    Convert from HTML entities (named or numeric) to Unicode characters.
    """
    def fixup(m):
        """
        Given an HTML entity (named or numeric), return its Unicode equivalent.
        Does not, however, unescape &lt; &gt; and &amp; (decimal 60, 62, and
        38). Those are 'special' in that they are often escaped for very
        important, specific reasons (e.g. to describe HTML within HTML). Any
        messing with them is likely to break things badly.
        """
        text = m.group(0)
        if text[:2] == "&#":            # numeric entity
            try:
                codepoint = int(text[3:-1], 16) if text[:3] == "&#x" \
                            else int(text[2:-1])
                if codepoint != 38 and codepoint != 60 and codepoint != 62:
                    return unichr(codepoint)
            except ValueError:
                pass
        else:                           # named entity
            try:
                codepoint = name2codepoint[text[1:-1]]
                if codepoint != 38 and codepoint != 60 and codepoint != 62:
                    return unichr(codepoint)
            except KeyError:
                pass
        return text                     # leave as is

    return re.sub(r"&#?\w+;", fixup, text)

unicode_entities = unescape            # alias for parallel name structure


def named_entities_codec(text):
    """
    Encode codec that converts Unicode characters into named entities (where
    the names are known), or failing that, numerical entities.
    """
    if isinstance(text, (UnicodeEncodeError, UnicodeTranslateError)):
        s = []
        for c in text.object[text.start:text.end]:
            if ord(c) in codepoint2name:
                s.append(NAMED_ENT.format(codepoint2name[ord(c)]))
            else:
                s.append(NUMERIC_ENT.format(ord(c)))
        return ''.join(s), text.end
    else:
        raise TypeError("Can't handle {0}".format(text.__name__))


def numeric_entities_codec(text):
    """
    Encode codec that converts Unicode characters into numeric entities.
    """
    if isinstance(text, (UnicodeEncodeError, UnicodeTranslateError)):
        s = []
        for c in text.object[text.start:text.end]:
            s.append(NUMERIC_ENT.format(ord(c)))
        return ''.join(s), text.end
    else:
        raise TypeError("Can't handle {0}".format(text.__name__))


def hex_entities_codec(text):
    """
    Encode codec that converts Unicode characters into numeric entities
    in hexadecimal form.
    """
    if isinstance(text, (UnicodeEncodeError, UnicodeTranslateError)):
        s = []
        for c in text.object[text.start:text.end]:
            s.append(NUMERIC_ENT.format(hex(ord(c))[1:]))
        return ''.join(s), text.end
    else:
        raise TypeError("Can't handle {0}".format(text.__name__))


codecs.register_error('named_entities',   named_entities_codec)
codecs.register_error('numeric_entities', numeric_entities_codec)
codecs.register_error('hex_entities',     hex_entities_codec)


def named_entities(text):
    """
    Given a string, convert its Unicode characters and numerical HTML entities
    to named HTML entities. Works by converting the entire string to Unicode
    characters, then re-encoding Unicode characters into named entities.
    Where names are not known, numerical entities are used instead.
    """
    unescaped_text = unescape(text)
    entities_text = unescaped_text.encode('ascii', 'named_entities')
    if _PY3:
        # we don't want type bytes back, we want str; therefore...
        return entities_text.decode("ascii", "strict")
    else:
        return entities_text


def numeric_entities(text):
    """
    Given a string, convert its Unicode characters and named HTML entities
    to numeric HTML entities. Works by converting the entire string to Unicode
    characters, then re-encoding Unicode characters into numeric entities.
    """
    unescaped_text = unescape(text)
    entities_text = unescaped_text.encode('ascii', 'numeric_entities')

    if _PY3:
        # we don't want type bytes back, we want str; therefore...
        return entities_text.decode("ascii", "strict")
    else:
        return entities_text


def numeric_entities_builtin(text):
    """
    Given a string, convert its Unicode characters and named HTML entities
    to numeric HTML entities. Works by converting the entire string to Unicode
    characters, then re-encoding Unicode characters into numeric entities.

    This one uses the xmlcharrefreplace builtin.
    """
    unescaped_text = unescape(text)
    entities_text = unescaped_text.encode('ascii', 'xmlcharrefreplace')

    if _PY3:
        # we don't want type bytes back, we want str; therefore...
        return entities_text.decode("ascii", "strict")
    else:
        return entities_text


def hex_entities(text):
    """
    Given a string, convert its Unicode characters and named HTML entities to
    numeric HTML entities written in hexadecimal form. Works by converting the
    entire string to Unicode characters, then re-encoding Unicode characters
    into numeric entities.
    """
    unescaped_text = unescape(text)
    entities_text = unescaped_text.encode('ascii', 'hex_entities')

    if _PY3:
        # we don't want type bytes back, we want str; therefore...
        return entities_text.decode("ascii", "strict")
    else:
        return entities_text


def encode_ampersands(text):
    """
    Encode ampersands into &amp;
    """
    text = re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', text)
    return text
