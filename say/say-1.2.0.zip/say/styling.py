"""
Module to handle styled printing
"""

import six
from colors import color as _color, COLORS, STYLES
if six.PY3:
    unicode = str

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

def styledef(*args, **kwargs):
    """
    Return a lambda that implements the given style definition.
    First named color is foreground, second is background. Styles
    can be named anywhere.
    """
    kw = {}
    for arg in args:
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
