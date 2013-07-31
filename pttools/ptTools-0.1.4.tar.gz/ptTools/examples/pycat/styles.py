#!/usr/bin/env python3

"""Styles for pycat.py."""

import ptTools
from ptTools.writers.ansiwriter import BLINK as blink
from ptTools.writers.ansiwriter import BOLD as bold
from ptTools.writers.ansiwriter import COLOR as color
from ptTools.writers.ansiwriter import UNDERLINE as underline
from ptTools.writers.ansiwriter import COLORS as colors

from collections import namedtuple

prio = 'priority'
"""Precedence weigth for a style description."""

rainbow = (4, 1, 2, 7, 9, 10, 12)
"""Color indices for nested parenthesis."""

styles = {

    ## Default
    'default'  : { underline : False,
                   bold : False,
                   color : 7,
                   blink : False,
                   prio : 0,
                   },
    
    ## Types
    'string'   : { color : 6, prio : 1 }, 
    'number'   : { color : 7, prio : 1 },

    ## Keywords
    'keyword'  : { color : 5, prio : 2 },
    'self'     : { color : 12, bold : True, prio : 3 },
    'super'    : { color : 12, bold : True, prio : 3 },
    'class'    : { color : 4,  bold : True, prio : 3 },
    'def'      : { color : 4,  bold : True, prio : 3 },
    'bool'     : { color : 1,  prio : 3 },    
    'import'   : { color : 1,  prio : 3 },
    'raise'    : { color : 1,  bold : True, prio : 3 },
    
    ## Operators
    'op'       : { color : 123,  prio : 2 },
    'boolop'   : { bold  : True, prio : 3 },
    'brace'    : { colors : rainbow, bold : True, prio : 3 },
    'bracket'  : { colors : rainbow, prio : 3 },
    'paren'    : { colors : rainbow, bold : True, prio : 3 },

    ## Comments
    ## The COMMENT key is defined/required by AnsiParseTreeWriter.
    'comment'        : { color : 240, prio : 2 },
    'mod_comment'    : { color : 239, prio : 3 },
    'class_comment'  : { color : 239, prio : 3 },
    'def_comment'    : { color : 239, prio : 3 },
    'multi_comment'  : { color : 239, underline : True, prio : 3 },
    
    ## Names
    'class_name'    : { color : 2, bold : True, prio : 2 },
    'def_name'      : { color : 2, prio : 2 },
    'imported_name' : { color : 1, underline : True, prio : 2 },
    'raised_name'   : { color : 2, bold : True, prio : 2 },

    ## Parameters
    'parameter' : { color : 123, prio : 4 },
    'arglist'   : { color : 3, bold : True, prio : 4 },

    ## Other
    'decorator'        : { color : 1, underline : True, prio : 2 },
    'exceeding_length' : { color : 1, blink : True, prio : 5 },
    'debug'            : { color : 123, blink : True, prio : 6,
                           underline : False, colors : rainbow },
    }


def style_node(key, fn=None):
    """Returns function that adds an attribute to node."""
    def setter(node):
        if fn:
            sty = fn(styles[key])
        else:
            sty = styles[key]
        if any((n.get_attribute(prio, 0) > sty[prio] for n in node.ancestors)):
            return
        else:
            node.add_attributes(sty)
    return setter

def style_token(key):
    """Returns function that adds an attribute to node."""
    def setter(token):
        sty = styles[key]
        token.add_attributes(sty)
    return setter
    
def style_depth(node):
    """Determines and sets the color attribute of node, dependent on
    the depth of nested parenthesis, brackets and braces."""
    def get_depth(token):
        """Returns depth attribute of token if present, else
        calculates, sets, and returns it."""
        if token.has_attribute('depth'):
            depth = token.get_attribute('depth')
            return depth+1 if token.string in '([{' else depth
        elif token.predecessor:
            prevd = get_depth(token.predecessor)
            depth = prevd-1 if token.string and token.string in ')]}' else prevd
            token.add_attributes({'depth' : depth})
            return depth
        else:
            return 0
    depth = get_depth(node.tokens[-1])
    clrs = node.attributes[colors]
    idx = min(len(clrs)-1, depth)
    assert(idx >= 0)
    node.attributes[color] = clrs[idx]

