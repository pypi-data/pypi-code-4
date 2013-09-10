"""Interpolating string formatter. """

import string
import inspect
import sys
import os
import re
from stuf import chainstuf
from options import Options, OptionsContext
import six
from textwrap import fill, dedent
from say.util import *

stdout = sys.stdout
stderr = sys.stderr

### Workhorse functions

sformatter = string.Formatter()  # piggyback Python's format() template parser


def _sprintf(arg, caller, override=None):
    """
    Format the template string (arg) with the values seen in the context of the
    caller. If override is defined, it is a Mapping providing additional values
    atop those of the local context.
    """

    def seval(s):
        """
        Evaluate the string s in the caller's context. Return its value.
        """
        try:
            localvars = caller.f_locals if override is None \
                                        else chainstuf(override, caller.f_locals)
            return eval(s, caller.f_globals, localvars)
        except SyntaxError:
            raise SyntaxError("syntax error when formatting '{0}'".format(s))

    if is_string(arg):
        parts = []
        for (literal_text, field_name, format_spec, conversion) in sformatter.parse(arg):
            parts.append(literal_text)
            if field_name is not None:
                format_str = six.u("{0") + ("!" + conversion if conversion else "") + \
                                          (":" + format_spec if format_spec else "") + "}"
                field_value = seval(field_name)
                formatted = format_str.format(field_value)
                parts.append(formatted)
        return ''.join(parts)
    else:
        return str(seval(str(arg)))


### Core Say class

class Say(object):

    """
    Say encapsulates printing functions. Instances are configurable, and callable.
    """
    
    options = Options(  
        indent=0,           # indent level (if set to None, indentation is turned off)
        indent_str='    ',  # indent string for each level
        encoding=None if six.PY3 else 'utf-8',
                            # character encoding for output (needed on Python 2, not 3)
        encoded=None,       # character encoding to return
        files= [stdout],    # where is output headed? a list of write() able objects
                            # NB Set to [stdout] but in way that gets around stuf bug
        wrap=None,          # column to wrap text to, if any
        sep=' ',            # separate args with this (Python print function compatible)
        end='\n',           # end output with this (Python print function compatible)
        silent=False,       # do the formatting and return the result, but don't write the output
        retvalue=False,     # should return the value of the formatted string?
        _callframe=None,    # frome from which the caller was calling
    )

    options.magic(
        indent = lambda v, cur: cur.indent + int(v) if isinstance(v, str) else v
    )

    def __init__(self, **kwargs):
        """
        Make a say object with the given options.
        """
        self.options = Say.options.push(kwargs)

    @staticmethod
    def escape(s):
        """
        Double { and } characters in a string to 'escape' them so ``str.format``
        doesn't treat them as template characters. NB This is NOT idempotent!
        Escaping more than once (when { or } are present ) = ERROR.
        """
        return s.replace('{', '{{').replace('}', '}}')

    def hr(self, sep=six.u('\u2500'), width=40, vsep=0, **kwargs):
        """
        Print a horizontal line. Like the HTML hr tag. Optionally
        specify the width, character repeated to make the line, and vertical separation.
        
        Good options for the separator may be '-', '=', or parts of the Unicode 
        box drawing character set. http://en.wikipedia.org/wiki/Box-drawing_character
        """
        opts = self.options.push(kwargs)

        self.blank_lines(vsep, **opts)
        self._output([sep * width], opts)
        self.blank_lines(vsep, **opts)

    def title(self, name, sep=six.u('\u2500'), width=15, vsep=0, **kwargs):
        """
        Print a horizontal line with an embedded title. 
        """
        opts = self.options.push(kwargs)
        if not opts._callframe:
            opts._callframe = inspect.currentframe().f_back
        
        formatted = _sprintf(name, opts._callframe) if is_string(name) else str(name)

        self.blank_lines(vsep, **opts)
        line = sep * width
        self._output([ ' '.join([line, formatted, line]) ], opts)
        self.blank_lines(vsep, **opts)

    def blank_lines(self, n, **kwargs):
        """
        Output N blank lines ("vertical separation")
        """
        if n > 0:
            opts = self.options.push(kwargs)
            self._write("\n" * n, opts)

    def set(self, **kwargs):
        """
        Permanently change the reciver's settings to those defined in the kwargs.
        An update-like function.
        """
        self.options.set(**kwargs)

    def setfiles(self, files):
        """
        Set the list of output files. ``files`` is a list. For each item, if
        it's a real file like ``sys.stdout``, use it. If it's a string, assume
        it's a filename and open it for writing. 
        """
        def opened(f):
            """
            If f is a string, consider it a file name and return it, ready for writing.
            Else, assume it's an open file. Just return it.
            """
            return open(f, "w") if is_string(f) else f

        self.options.files = [opened(f) for f in files]
        return self

        # TBD: Turn this into 'magical' attribute set

    def settings(self, **kwargs):
        """
        Open a context manager for a `with` statement. Temporarily change settings
        for the duration of the with.
        """
        return SayContext(self, kwargs)

    def clone(self, **kwargs):
        """
        Create a new Say instance whose options are chained to this instance's
        options (and thence to Say.options). kwargs become the cloned instance's
        overlay options.
        """
        cloned = Say()
        cloned.options = self.options.push(kwargs)
        return cloned

    def __call__(self, *args, **kwargs):
        """
        Primary interface. say(something)
        """

        opts = self.options.push(kwargs)
        if not opts._callframe:
            opts._callframe = inspect.currentframe().f_back
        
        formatted = [ _sprintf(arg, opts._callframe) if is_string(arg) else str(arg)
                      for arg in args ]
        return self._output(opts.sep.join(formatted), opts)

    def __gt__(self, arg):
        """
        Simple, non-functional call. Experimental.  
        """

        opts = self.options.push({})
        opts._callframe = inspect.currentframe().f_back
        
        formatted = [ _sprintf(arg, opts._callframe) if is_string(arg) else str(arg) ]
        return self._output(opts.sep.join(formatted), opts)

    def _output(self, data, opts):
        """
        Do the actual formatting and outputting work. ``data`` may be either a
        list of lines, or a composed string.
        """

        if opts.indent or opts.wrap:
            indent_str = opts.indent_str * opts.indent
            if opts.wrap:
                datastr = '\n'.join(data) if isinstance(data, list) else data
                outstr = fill(datastr, width=opts.wrap, initial_indent=indent_str, subsequent_indent=indent_str)
            else:
                datalines = data if isinstance(data, list) else data.splitlines()
                outstr = '\n'.join([ ''.join([ indent_str, line ]) for line in datalines ])
        else:
            outstr = '\n'.join(data) if isinstance(data, list) else data
        # by end of indenting, dealing with string only

        # prepare and emit output
        if opts.end is not None:
            outstr += opts.end
        if not opts.silent:
            to_write = encoded(outstr, opts.encoding)
            self._write(to_write, opts)

        # prepare and return return value
        if opts.retvalue:
            retencoding = opts.encoding if opts.encoded is True else opts.encoded
            retencoded = encoded(outstr, retencoding)
            rettrimmed = retencoded[:-1] if retencoded.endswith('\n') else retencoded
            return rettrimmed

    def _write(self, s, opts):
        """
        Write s to all associated file objects. 
        """
        # print(opts)
        for f in opts.files:
            f.write(s)


class SayContext(OptionsContext):

    """
    Context helper to support Python's with statement.  Generally called
    from ``with say.settings(...):``
    """
    pass


### Define default ``say`` and ``fmt`` callables

say = Say()

fmt = Say(encoding=None, retvalue=True, silent=True)
fmt.setfiles([])

# TODO: fmt() is such a core feature - maybe a subclas not just an
# instance configuration?


def caller_fmt(*args, **kwargs):
    """
    Like fmt(), but iterpolating strings not from the caller's context, but the caller's caller's
    context.  It sounds uber meta, but it helps easily make other routines be able to do what
    fmt() can do.
    """
    kwargs['_callframe'] = inspect.currentframe().f_back.f_back
    return fmt(*args, **kwargs)
    
