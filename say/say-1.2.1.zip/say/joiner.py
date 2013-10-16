"""
Module to assist in the super-common operation of
joining values in sequences into strings.
"""

import re
from options import Options
import six

def is_string(v):
    return isinstance(v, six.string_types)

def stringify(v):
    """
    Return a string. If it's already a string, just return that.
    Otherwise, stringify it.
    """
    return v if is_string(v) else str(v)

def blanknone(v):
    """
    Return a value, or empty string if it's None.
    """
    return '' if v is None else v

joiner_options = Options(
    sep = ', ',    # separator between items
    twosep=None,   # separator between items if only two
    lastsep=None,  # separator between penultimate and final item
    quoter=None,   # quoter for individual items
    endcaps=None,  # quoter for entire joined sequence
    prefix=None,   # prefix for entire joined, endcaped sequence
    suffix=None    # suffix for entire joined, endcaped sequence
)

def joiner(seq, **kwargs):
    """
    Join the items of a sequence into a string. Implicitly stringifies any
    not-string values. Allows specification of the separator between items (and
    a special case for the last separator). Allows each item to be optionally
    quoted by a function, and the entire list to be optionally quoted with an
    endcaps function. A separate suffix and prefix may also be provdied.
    """

    opts = joiner_options.push(kwargs)

    def prep(v):
        """
        Prepare an item by stringifying and optionally quoting it.
        """
        s = stringify(v)
        return opts.quoter(s) if opts.quoter else s

    seqlist = list(seq)
    length = len(seqlist)
    if length == 0:
        core = ''
    elif length == 1:
        core = prep(seqlist[0])
    elif length == 2 and opts.twosep:
        sep = opts.twosep if opts.twosep is not None else opts.sep
        core = sep.join(prep(v) for v in seqlist)
    else:
        start = [ prep(v) for v in seqlist[:-1] ]
        final = prep(seqlist[-1])
        if opts.lastsep is None:
            opts.lastsep = opts.sep
        core = opts.lastsep.join([ opts.sep.join(start), final])
    capped = opts.endcaps(core) if opts.endcaps else core
    if opts.prefix or opts.suffix:
        affixed = ''.join([ blanknone(opts.prefix), capped, blanknone(opts.suffix) ])
    else:
        affixed = capped
    return affixed

def word_join(seq, **kwargs):
    """
    Slightly specific joiner for words. Returns by default an Oxford comma list,
    but accepts all the same options as joiner.
    """
    kwargs.setdefault('sep', ', ')
    kwargs.setdefault('twosep', ' and ')
    kwargs.setdefault('lastsep', ', and ')
    return joiner(seq, **kwargs)

join = joiner
and_join = word_join

def or_join(seq, **kwargs):
    """
    A, B, or C.
    """
    kwargs.setdefault('sep', ', ')
    kwargs.setdefault('twosep', ' or ')
    kwargs.setdefault('lastsep', ', or ')
    return joiner(seq, **kwargs)

#def is_sequence(arg):
#    return (not hasattr(arg, "strip") and
#            hasattr(arg, "__getitem__") or
#            hasattr(arg, "__iter__"))



concat_options = joiner_options.add(
    sep = '', # combine with no separator, by default
)

def concat(*args, **kwargs):
    six.print_("kwargs:", kwargs)
    six.print_("concat_options:", concat_options)
    opts = concat_options.push(kwargs)
    six.print_("opts:", opts)
    six.print_("args:", args)

    args=list(args)
    six.print_("listed args:", args)

    if len(args) == 1 and is_sequence(args):
        args = list(args[0])
    six.print_("args:", args)
    six.print_("opts:", opts)
    return joiner(args, **opts)  # problem here in Py3x

items_options = Options(
    sep = "\n",  # separator between items
    fmt = "{key}: {value!r}",
    header = None,   # header for entire list
    footer = None    # footer for entire list
)

def iter_items(items):
    if hasattr(items, 'items'):  # dict or mapping
        for k, v in items.items():
            yield k, v
    else:
        for k, v in enumerate(items):
            yield k, v

def items(seq, **kwargs):
    opts = items_options.push(kwargs)

    formatted_items = [ opts.fmt.format(key=k, value=v) for k,v in iter_items(seq) ]
    items_str = opts.sep.join(formatted_items)
    if opts.header or opts.footer:
        parts = []
        if opts.header:
            parts.extend([opts.header, opts.sep])
        parts.append(items_str)
        if opts.footer:
            parts.extend([opts.sep, opts.footer])
        items_str = ''.join(parts)
    return items_str
