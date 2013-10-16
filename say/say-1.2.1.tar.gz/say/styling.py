"""
Module to handle styled printing
"""

import six
from colors import color as _color, COLORS, STYLES
from stuf import stuf
if six.PY3:
    unicode = str

QUOTE_DELIM = ('"', "'")
QUOTE_DELIM_STR = ''.join(QUOTE_DELIM)

# TODO: implement a persistent Style object that say.style will return
# TODO: implement own six-like features, rather than hanging between six and custom code

class optdict(dict):
    """
    dict subclass that only initializes those keys where there's a non-empty value.
    Convenient for creating kwarg dicts that don't have to define default values.
    """
    def __init__(self, **kwargs):
        dict.__init__(self)
        for k,v in kwargs.items():
            if v:
                self[k] = v


class StyleDef(object):
    """
    Class defining a formatting style.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a new StyleDef, remembering its settings.
        """
        self.name = kwargs.get('name', None)
        self.sdef = styledef(*args, **kwargs)
        self.join = kwargs.get('join', None)

    def __call__(self, item):
        """
        Apply this style to the given item.
        """
        result = self.join(item) if self.join else item
        result = _color(result, **self.sdef) if self.sdef else result
        return result

def styledef(*args, **kwargs):
    """
    Parses a style definition as given in args and kwargs.
    Return a dict that defines a given style definition. If it's an ANSI style
    being defined, whatever color is named first (if any) is assumed to be the
    foreground, the second the background. ANSI display styles (like 'bold') can
    be named anywhere.
    """
    kw = stuf()
    for arg in args:
        # print "ARG:", arg
        arg = arg.replace('+', '|').replace(',', '|').lower()
        parts = [p.strip() for p in arg.split('|')]
        fg, bg, styles = None, None, []
        for p in parts:
            if p in COLORS:
                if not fg:
                    fg = p
                elif not bg:
                    bg = p
                else:
                    raise ValueError('only fg and bg colors!')
            elif p in STYLES:
                styles.append(p)
        kw.update(optdict(fg=fg, bg=bg, style='|'.join(styles) if styles else None))
    kw.update(kwargs)
    # print "KW:", kw
    return kw

def autostyle(*args, **kwargs):
    """
    Return a lambda that will later format a string with the given styledef.
    """
    sdef = styledef(*args, **kwargs)
    return lambda x: color(x, **sdef)

def color(item, **kwargs):
    """
    Like colors.color, except auto-casts to Unicode string if need be.
    """
    item_u = unicode(item) if not isinstance(item, six.string_types) else item
    return _color(item_u, **kwargs)

def styled(item, *args, **kwargs):
    """
    Like color, but can also include style names.
    Kind of an immediate-mode version of autostyle.
    """
    sdef = styledef(*args, **kwargs)
    return color(item, **sdef)
