#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""katagami: a simple xml/html template library
============================================

This library is one of many `Python templating libraries
<http://wiki.python.org/moin/Templating>`_.


Features
--------
 * Based on XML's Processing instructions (`<?...?>`)
 * Simple features and simple implementation
 * Python script inside XML/HTML with any level indentation
 * `Inline Python expression`_
 * `Embed Python script`_
 * `Block structure`_
 * Supports both of Python 2 and Python 3
 * As fast as `mako <http://www.makotemplates.org/>`_


Example
-------

Make a HTML string with `inline Python expression`_ and Python's `for` (`Block
structure`_)::

    >>> from katagami import render_string
    >>> print(render_string('''<html>
    ... <body>
    ...     <? for name in names: {?>
    ...         <p>hello, <?=name?></p>
    ...     <?}?>
    ... </body>
    ... </html>''', {'names': ['world', 'python']}))
    <html>
    <body>
    <BLANKLINE>
            <p>hello, world</p>
    <BLANKLINE>
            <p>hello, python</p>
    <BLANKLINE>
    </body>
    </html>


Inline Python expression
------------------------

This feature evaluates your inline expression and output to result::

    >>> print(render_string('''<html><body>
    ...     <?='hello, world'?>
    ... </body></html>'''))
    <html><body>
        hello, world
    </body></html>

By the default, this example raises an exception, evaluated expression must be
`str` (`unicode` in Python 2)::

    >>> print(render_string('''<html><body>
    ...     <?=1?>
    ... </body></html>'''))
    Traceback (most recent call last):
    ...
    TypeError: Can't convert 'int' object to str implicitly

Set the `cast_string` feature::

    >>> print(render_string('''<?py
    ...         from katagami import cast_string
    ...     ?><html><body>
    ...     <?=1?>
    ... </body></html>'''))
    <html><body>
        1
    </body></html>

Also set the `except_hook` feature::

    >>> print(render_string('''<?py
    ...         from katagami import except_hook
    ...     ?><html><body>
    ...     <?=1?>
    ... </body></html>'''))
    <html><body>
        Can't convert 'int' object to str implicitly
    </body></html>


Embed Python script
-------------------

All indentation will be arranged automatically::

    >>> print(render_string('''<html>
    ... <?py
    ...     # It is a top level here. This works fine.
    ...     if 1:
    ...         msg = 'message from indented script'
    ... ?>
    ... <body>
    ...     <p><?=msg?></p>
    ...     <?py msg = 'message from single line script' # This works fine too. ?>
    ...     <p><?=msg?></p>
    ...     <? if 1: {?>
    ... <?py
    ... # Is is nested here. This also works fine.
    ... msg = 'message from nested indented script'
    ... ?>
    ...     <p><?=msg?></p>
    ...     <?}?>
    ... </body>
    ... </html>'''))
    <html>
    <BLANKLINE>
    <body>
        <p>message from indented script</p>
    <BLANKLINE>
        <p>message from single line script</p>
    <BLANKLINE>
    <BLANKLINE>
        <p>message from nested indented script</p>
    <BLANKLINE>
    </body>
    </html>


Block structure
---------------

Indentation with C-style block structure::

    >>> print(render_string('''<html>
    ... <body>
    ...     <p>hello,&nbsp;
    ...     <? try: {?>
    ...         <?=name?>
    ...     <?} except NameError: {?>
    ...         NameError
    ...     <?} else: {?>
    ...         never output here
    ...     <?}?>
    ...     </p>
    ... </body>
    ... </html>'''))
    <html>
    <body>
        <p>hello,&nbsp;
    <BLANKLINE>
    <BLANKLINE>
            NameError
    <BLANKLINE>
        </p>
    </body>
    </html>

Note
~~~~

 * '<? }' and '{ ?>' are wrong. Don't insert space. '<?}' and '{?>' are correct.
 * Ending colon (':') is required.
 * Block closing '<?}?>' is required.


Encoding detection
------------------

Encoding will be detected automatically::

    >>> print(render_string(b'''<html>
    ... <head><meta charset="shift-jis"></head>
    ... <body>\x93\xfa\x96{\x8c\xea</body>
    ... </html>'''))
    <html>
    <head><meta charset="shift-jis"></head>
    <body>\u65e5\u672c\u8a9e</body>
    </html>

Supported formats:

 * <?xml encoding="ENCODING"?>
 * <meta charset="ENCODING">
 * <meta http-equiv="Content-Type" content="MIMETYPE; ENCODING">


History
-------

 * 2.0.0 changes a lot and add some features
 * 1.1.0 change api, add except_handler, add shorthand of gettext (<?_message?>),
         some fixes
 * 1.0.3 fix ignoring `encoding` argument, fix indent bug, add `renderString`
 * 1.0.2 improve doctest compatibility, some fixes
 * 1.0.1 fix bugs, docs, speed
 * 1.0.0 remove backward compatibility
"""
from __future__ import print_function, unicode_literals, division

__version__ = '2.0.0'
__author__ = __author_email__ = 'chrono-meter@gmx.net'
__license__ = 'PSF'
__url__ = 'http://pypi.python.org/pypi/katagami'
# http://pypi.python.org/pypi?%3Aaction=list_classifiers
__classifiers__ = [i.strip() for i in '''\
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: Python Software Foundation License
    Operating System :: OS Independent
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: Text Processing :: Markup :: HTML
    Topic :: Text Processing :: Markup :: XML
    '''.strip().splitlines()]
    #Development Status :: 5 - Production/Stable

import sys
import time
import re
import io
import tokenize
import logging; logger = logging.getLogger(__name__); del logging
from gettext import gettext as _


__all__ = (
    'render_file',
    'render_string',
    'render_resource',
    'returns_bytes',
    'returns_iter',
    'returns_renderer',
    )
features = (
    'cast_string',
    'except_hook',
    )
TAB = '    '
PREFIX, SUFFIX = '<?', '?>'
returns_bytes = 1
returns_iter = 2
returns_renderer = 4
cast_string = 10
except_hook = 20

notgiven = object()
def dbg(*a, **k): print(*a, file=sys.stderr, **k)

if sys.version < '2.7':
    raise RuntimeError('not supported version: %s' % sys.version)
if sys.version < '3':
    # TODO: python2 doctest compatibility
    # doctest compatibility with Python 2 and Python 3
    __doc__ = re.sub(
        "Can't convert '(.*?)' object to str implicitly",
        "Can't convert '\\1' object to unicode implicitly",
        __doc__)
    BytesType = str
    StringType = unicode
    def next(generator):
        return generator.next()
else:
    BytesType = bytes
    StringType = str


def execcode(code, globals):
    """This function resolves this problem in Python 2::
        SyntaxError: unqualified exec is not allowed in function it is a nested function
    """
    exec(code, globals)


def u(s):
    return '"%s"' % s.encode('unicode_escape').decode().replace('"', '\\"')


def makedict(*originals, **kwargs):
    r"""Make a dict and update with arguments.

    >>> sorted(makedict({'a': 1}, {'b': 2}, c=3).items())
    [('a', 1), ('b', 2), ('c', 3)]
    """
    result = {}
    for i in originals:
        if i:
            result.update(i)
    result.update(kwargs)
    return result


def decorate_attributes(**kwargs):
    """attributes decorator"""
    def result(function):
        for i in kwargs.items():
            setattr(function, *i)
        return function
    return result


def set_pyindent(source, indent=''):
    r"""Remove comments and justify indentation.

    >>> print(set_pyindent('''
    ... # comment
    ...     a
    ...     if 1:
    ...         b
    ...     '''))
    <BLANKLINE>
    <BLANKLINE>
    a 
    if 1 :
        b 
    <BLANKLINE>

    >>> print(set_pyindent('''
    ... # comment
    ...     a
    ...     if 1:
    ...         b
    ...     ''', TAB * 2))
    <BLANKLINE>
    <BLANKLINE>
            a 
            if 1 :
                b 
    <BLANKLINE>
    """
    tokens = []
    first_indent = None

    # NOTE: Is this bug of tokenize.untokenize() ?
    if not source.startswith('\n'):
        source = '\n' + source

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        # token = (type, string, start, end, line)

        # skip comment
        if token[0] in (tokenize.COMMENT, ):
            continue

        # firstmost indent found
        if first_indent is None:
            if token[0] == tokenize.INDENT:
                first_indent = token[1]
            # NOTE: no tokenize.ENCODING in python2
            elif token[0] in (tokenize.NEWLINE, tokenize.NL):
                pass
            else:
                first_indent = ''

        # string = indent string starts from beggining of the line
        if token[0] == tokenize.INDENT:
            if first_indent:
                assert token[1].startswith(first_indent)
                token = token[0], indent + token[1][len(first_indent):]
            else:
                token = token[0], indent + token[1]
        # elif token[0] == tokenize.DEDENT:
            # pass
        else:
            token = token[:2]

        tokens.append(token)

    if not first_indent:
        tokens.insert(0, (tokenize.INDENT, indent))

    return tokenize.untokenize(tokens)


def firstlinetokens(source):
    r"""Get the firstline tokens.

    >>> ' '.join(token[1] for token in firstlinetokens('''
    ...     # comment
    ...     "docstring"
    ...     some_statement
    ...     '''))
    'some_statement'
    """
    result = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        # token = (type, string, start, end, line)

        # skip comment and docstring
        if token[0] in (tokenize.NL, tokenize.INDENT, tokenize.COMMENT,
                        tokenize.STRING, ):
            continue
        elif token[0] == tokenize.NEWLINE:
            if result:
                break
        else:
            result.append(token)

    return result


def detect_encoding(bytes):
    r"""Search xml/html encoding and return it.

    >>> detect_encoding(b'<?xml version="1.0" encoding="UTF-8"?>')
    'UTF-8'
    >>> detect_encoding(b"<?xml version='1.0' encoding='UTF-8'?>")
    'UTF-8'
    >>> detect_encoding(b'<?xml version=1.0 encoding=UTF-8?>')
    'UTF-8'

    >>> detect_encoding(b'<meta charset="UTF-8">')
    'UTF-8'
    >>> detect_encoding(b"<meta charset='UTF-8'>")
    'UTF-8'
    >>> detect_encoding(b'<meta charset=UTF-8>')
    'UTF-8'

    >>> detect_encoding(b'<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">')
    'UTF-8'
    >>> detect_encoding(b"<meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>")
    'UTF-8'
    """
    encoding_patterns = (
        # <?xml encoding="utf-8"?>
        (b'<\?xml\\s+.*?encoding=["\']?([^\\s"\']+)["\']?.*?\?>', ),
        # <meta charset="UTF-8">
        # <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        (b'<meta\\s+.*?charset=["\']?([^\\s"\']+)["\']?.*?>', ),
        )

    if not isinstance(bytes, BytesType):
        bytes = bytes.encode('ascii', 'ignore')

    for pattern in encoding_patterns:
        # dbg(pattern)
        s = bytes
        match = None
        for i in pattern:
            match = re.search(i, s, re.DOTALL | re.IGNORECASE)
            if not match:
                break
            s = match.group(0)
        if match and match.group(1):
            return match.group(1).decode()

    return 'utf-8'


class Cache(dict):
    r"""Dict with maximum items length limitation and time based expiration.

    >>> cache = Cache()
    >>> cache.max_length = 2
    >>> cache.expiration = 0.100 # 100 millisecond

    Test max_length:
    >>> cache[1] = 1
    >>> time.sleep(0.001)
    >>> cache[2] = 2
    >>> time.sleep(0.001)
    >>> cache[3] = 3
    >>> cache.max_length >= len(cache)
    True

    Test expiration:
    >>> time.sleep(0.150)
    >>> cache[3]
    Traceback (most recent call last):
        ...
    KeyError: 3
    """
    # in seconds, check that file is updated when time is expired.
    expiration = -1
    # maximum cached objects count
    max_length = 1000

    def __getitem__(self, key):
        generated, result = super(Cache, self).__getitem__(key)
        if self.expiration > 0 and time.time() > generated + self.expiration:
            del self[key]
            raise KeyError(key)
        return result

    def __setitem__(self, key, value):
        if len(self) > self.max_length - 1:
            for k, v in sorted(self.items(), key=lambda i: i[1][0]):
                if len(self) <= self.max_length - 1:
                    break
                del self[k]
        super(Cache, self).__setitem__(key, (time.time(), value))


class Template(object):

    def __init__(self, file):
        self._makescript(file)
        self.code = compile(self.script, self.name, 'exec')
        # NOTE: except SyntaxError: traceback.print_exc(0)

    def _exectamplate(self, frame, flags=0):
        # python2 doesn't allow using return and yield in same function
        execcode(self.code, frame)

        executor = frame['__main__']()
        if executor is None: # The template is empty or that has only scripts.
            raise StopIteration

        try:
            value = notgiven
            while 1:
                if value is notgiven:
                    value = next(executor)
                    if not isinstance(value, StringType):
                        if self.features & cast_string:
                            f = executor.gi_frame
                            if f and '__cast_string__' in f.f_locals:
                                value = f.f_locals['__cast_string__'](value)
                            elif f and '__cast_string__' in f.f_globals:
                                value = f.f_globals['__cast_string__'](value)
                            else:
                                value = StringType(value)
                        else:
                            continue
                else:
                    value = executor.throw(
                        TypeError,
                        'Can\'t convert \'%s\' object to %s implicitly' % (
                            type(value).__name__, StringType.__name__))

                if flags & returns_bytes:
                    value = value.encode(self.encoding)
                yield value

                value = notgiven

        except StopIteration:
            pass
        executor.close()

    def __call__(self, frame, flags=0):
        """Render the template with given frame."""
        result = self._exectamplate(frame, flags)
        if flags & returns_iter:
            return result
        elif flags & returns_bytes:
            return BytesType().join(result)
        else:
            return StringType().join(result)

    def _makescript(self, file):
        """make a script string from a template file
        
         * `file` -- file-like object
         * `return` -- Python script string
        """
        if sys.version < '3':
            if not hasattr(file, 'read'):
                raise TypeError('%r is not supported type' % file)
        else:
            if not isinstance(file, io.IOBase):
                raise TypeError('%r is not supported type' % file)
 
        # read all
        content = file.read()

        # detect encoding
        encoding = getattr(file, 'encoding', '')
        if not encoding:
            try:
                encoding = detect_encoding(content)
            except Exception as e:
                logger.debug('an error skipped: %r', e)
            # check encoding registered in Python
            try:
                b'_'.decode(encoding)
            except LookupError:
                encoding = ''
        if not encoding:
            encoding = sys.getdefaultencoding()
            if encoding == 'ascii':
                encoding = 'utf-8'

        # cast string
        if isinstance(content, BytesType):
            content = content.decode(encoding)

        self.features = 0
        self.lines = []
        self.indent = []
        current = 0
        pattern = re.compile(
            re.escape(PREFIX) + '(?P<body>.*?)' + re.escape(SUFFIX), re.DOTALL)

        for match in pattern.finditer(content):
            # get pos
            _ = content[:match.start()].splitlines()
            self.pos = (len(_), len(_[-1]) + 1) if _ else (1, 1)
            del _

            start, end = match.span()
            chunk = content[current:start]
            if chunk:
                self.appendline('yield ' + u(chunk))
            current = end

            chunk = match.group('body')

            for i in sorted(i for i in dir(self) if i.startswith('_handle_')):
                handler = getattr(self, i)
                if re.match(handler.pattern, chunk):
                    handler(chunk)
                    break

            # not supported <?...?>
            else:
                chunk = PREFIX + chunk + SUFFIX
                self.appendline('yield ' + u(chunk))

        chunk = content[current:]
        if chunk:
            self.appendline('yield ' + u(chunk))

        if self.indent:
            raise SyntaxError(
                'brace is not closed: %s' % self.indent[-1])

        self.name = getattr(file, 'name', '<string>')
        self.encoding = encoding

        # make a script
        prefix = [
            '__file__ = %s' % u(getattr(file, 'name', '<string>')),
            # '__name__ = "__main__"',
            '__encoding__ = %s' % u(encoding),
            'def __main__():',
            # TODO: touch user variables (global) from __main__ (local)
            ]
        self.script = '\n'.join(prefix) + '\n' \
                    + '\n'.join(TAB + i for i in self.lines)

    def appendline(self, line):
        self.lines.append(TAB * len(self.indent) + line)

    # <?=...?>
    @decorate_attributes(pattern='^=')
    def _handle_inline_expression(self, chunk):
        r"""Inline Python expression.

        >>> render_string('hello, <?=name?>', {'name': 'world'})
        'hello, world'

        >>> render_string('hello, <?=name # hello ?>', {'name': 'world'})
        'hello, world'


        Without cast_string, except_hook:
        >>> render_string('''
        ...     hello, <?=name?>
        ...     ''', {'name': 1}).strip()
        Traceback (most recent call last):
            ...
        TypeError: Can't convert 'int' object to str implicitly

        With cast_string:
        >>> render_string('''<?py
        ...         from katagami import cast_string
        ...     ?>
        ...     hello, <?=name?>
        ...     ''', {'name': 1}).strip()
        'hello, 1'

        With except_hook:
        >>> render_string('''<?py
        ...         from katagami import except_hook
        ...     ?>
        ...     hello, <?=name?>
        ...     ''', {'name': 1}).strip()
        "hello, Can't convert 'int' object to str implicitly"


        Customize cast_string behavior:
        >>> render_string('''<?py
        ...         from katagami import cast_string
        ...         def __cast_string__(o):
        ...             "__cast_string__ must be return str (or unicode in Python 2)"
        ...             return '[%s]' % o
        ...     ?>
        ...     hello, <?=name?>
        ...     ''', {'name': 1}).strip()
        'hello, [1]'

        Give __cast_string__ via context:
        >>> render_string('''<?py
        ...         from katagami import cast_string
        ...     ?>
        ...     hello, <?=name?>
        ...     ''',
        ...     {'name': 1, '__cast_string__': lambda o: '<%s>' % o}).strip()
        'hello, <1>'

        Give __cast_string__ via default_context:
        >>> default_context['__cast_string__'] = lambda o: '(%s)' % o
        >>> render_string('''<?py
        ...         from katagami import cast_string
        ...     ?>
        ...     hello, <?=name?>
        ...     ''', {'name': 1}).strip()
        'hello, (1)'
        >>> del default_context['__cast_string__']


        Curtomize except_hook behavior:
        >>> render_string('''<?py
        ...         from katagami import except_hook
        ...         def __except_hook__(typ, val, tb):
        ...             "__except_hook__ must be return str (or unicode in Python 2)"
        ...             return '%s catched' % typ.__name__
        ...     ?>
        ...     hello, <?=name?>
        ...     ''', {'name': 1}).strip()
        'hello, TypeError catched'

        Give __except_hook__ via context:
        >>> render_string('''<?py
        ...         from katagami import except_hook
        ...     ?>
        ...     hello, <?=name?>
        ...     ''',
        ...     {'name': 1, '__except_hook__': lambda t, v, tb: str(v)}).strip()
        "hello, Can't convert 'int' object to str implicitly"

        Give __except_hook__ via default_context:
        >>> default_context['__except_hook__'] = lambda t, v, tb: str(v)
        >>> render_string('''<?py
        ...         from katagami import except_hook
        ...     ?>
        ...     hello, <?=name?>
        ...     ''', {'name': 1}).strip()
        "hello, Can't convert 'int' object to str implicitly"
        >>> del default_context['__except_hook__']
        """
        # except_hook is enabled
        if self.features & except_hook:
            chunk = set_pyindent('''
                try:
                    yield %s
                except:
                    if '__except_hook__' in locals():
                        yield locals()['__except_hook__'](
                            *__import__('sys').exc_info())
                    elif '__except_hook__' in globals():
                        yield globals()['__except_hook__'](
                            *__import__('sys').exc_info())
                    else:
                        yield %s(__import__('sys').exc_info()[1])
                ''' % (chunk[1:], StringType.__name__), TAB * len(self.indent))
            self.lines.extend(chunk.splitlines())

        # normal mode, except_hook is disabled
        else:
            chunk = set_pyindent(chunk[1:]).strip()
            self.appendline('yield ' + chunk)

    # <?py...?>
    @decorate_attributes(pattern='^py')
    def _handle_embed_script(self, chunk):
        r"""Embed Python script.

        Simple:
        >>> render_string('''
        ...     <?py
        ...         name = 'world'
        ...     ?>
        ...     hello, <?=name?>
        ...     ''').strip()
        'hello, world'

        Simple, different level indentation:
        >>> render_string('''
        ...     <?py
        ...         name = 'joe'
        ...     ?>
        ...     <?py
        ... name = 'world'
        ...     ?>
        ...     hello, <?=name?>
        ...     ''').strip()
        'hello, world'

        Nested with statement:
        >>> render_string('''
        ...     <? if 1: {?>
        ...         <?py
        ...             name = 'world'
        ...         ?>
        ...     <?}?>
        ...     hello, <?=name?>
        ...     ''').strip()
        'hello, world'

        Get feature flags from firstmost embedded script:
        >>> render_string('''<?py
        ...     # comment
        ...     "docstring"
        ...     from katagami import cast_string, except_hook
        ...     ?>
        ...     ''', flags=returns_renderer).features
        30
        >>> render_string('''<html><?py
        ...     # comment
        ...     "docstring"
        ...     from katagami import cast_string, except_hook
        ...     ?></html>
        ...     ''', flags=returns_renderer).features
        0
        """
        # top of the template and first-line is `from katagami import ***`
        if not self.lines:
            firstline = firstlinetokens(chunk[2:])
            if ' '.join(i[1] for i in firstline[:3]) == 'from %s import' % __name__:
                for token in firstline[3:]:
                    if token[0] == tokenize.NAME and token[1] in features:
                        self.features |= globals()[token[1]]

        chunk = set_pyindent(chunk[2:], TAB * len(self.indent))
        self.lines.extend(chunk.splitlines())

    # <?}...{?>
    @decorate_attributes(pattern='(^}|.*{$)')
    def _handle_indent(self, chunk):
        r"""Bridge Python and XML by brace.

        Simple, if-else:
        >>> render_string('''
        ...     <? if 1: {?>
        ...         hello, world
        ...     <?} else: {?>
        ...         hidden area
        ...     <?}?>
        ...     ''').strip()
        'hello, world'

        Nested:
        >>> render_string('''
        ...     <? if 1: {?>
        ...         <? if 1: {?>
        ...             hello, world
        ...         <?}?>
        ...     <?}?>''').strip()
        'hello, world'

        Simple, try-except-finally:
        >>> re.sub('\s+', ' ', render_string('''
        ...     hello,
        ...     <? try: {?>
        ...         <?=name?>
        ...     <?} except NameError: {?>
        ...         unknown
        ...     <?} finally: {?>
        ...         !
        ...     <?}?>
        ...     ''').strip())
        'hello, unknown !'
        """
        if chunk.startswith('}'):
            chunk = chunk[1:]
            try:
                self.indent.pop()
            except LookupError:
                raise IndentationError('brace is not started: %s' % self.pos)

        indent = None
        if chunk.endswith('{'):
            chunk = chunk[:-1]
            indent = self.pos

        chunk = chunk.strip()
        if chunk:
            assert chunk.split()[0] not in ('def', 'class')
            self.appendline(chunk)

        if indent:
            self.indent.append(indent)

    # <?\...?>
    @decorate_attributes(pattern='^\\\\')
    def _handle_escape(self, chunk):
        r"""Escape XML PIs.

        >>> render_string('<?\py "hello, world"?>')
        '<?py "hello, world"?>'
        """
        self.appendline('yield ' + u(PREFIX + chunk[1:] + SUFFIX))

    # <?_...?>
    @decorate_attributes(pattern='^_')
    def _handle_gettext(self, chunk):
        r"""Shorthand method for i18n.

        >>> render_string('<?_hello, world?>')
        'hello, world'
        """
        # self._handle_inline_expression('=_(%s)' % u(chunk[1:]))
        self.appendline('yield _(%s)' % u(chunk[1:]))


cache = Cache()
default_context = {
    '_': _,
    # '__except_hook__': function(type, value, traceback) -> 'error repr',
    # '__cast_string__': function(any_object) -> 'object repr',
    }


def set_common_default_context():
    import xml.sax.saxutils
    default_context.update(
        escape=xml.sax.saxutils.escape,
        quoteattr=xml.sax.saxutils.quoteattr,
        )


def render_file(file_or_filename, locals={}, flags=0):
    r"""Render a file-like object or a file.

     * `file_or_filename` -- file-like object or filename
     * `locals` -- variables for template execution context
     * `flags` -- Combination of these values: returns_bytes, returns_iter,
                                               returns_renderer.
    """
    cachekey = 'file', getattr(file_or_filename, 'name', file_or_filename)
    try:
        template = cache[cachekey]
    except LookupError:
        if isinstance(file_or_filename, StringType):
            file_or_filename = open(file_or_filename, 'rb')

        template = Template(file_or_filename)
        if cachekey:
            cache[cachekey] = template

    if flags & returns_renderer:
        assert not locals
        return template

    return template(makedict(default_context, locals), flags)


def render_string(string_or_bytes, locals={}, flags=0):
    r"""Render a string or a bytes.


    >>> tmpl = '<?="\u3053\u3093\u306b\u3061\u306f"?>'

    String-in, string-out:
    >>> render_string(tmpl)
    '\u3053\u3093\u306b\u3061\u306f'

    Bytes-in, string-out:
    >>> render_string(tmpl.encode('utf-8'))
    '\u3053\u3093\u306b\u3061\u306f'


    String-in, Bytes-out:
    >>> render_string(tmpl, flags=returns_bytes)
    b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf'

    Bytes-in, bytes-out:
    >>> render_string(tmpl.encode('utf-8'), flags=returns_bytes)
    b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf'

    String-in, string-iterator-out:
    >>> list(render_string(tmpl, flags=returns_iter))
    ['\u3053\u3093\u306b\u3061\u306f']

    String-in, bytes-iterator-out:
    >>> list(render_string(tmpl, flags=returns_bytes | returns_iter))
    [b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf']

    Bytes-in, string-iterator-out:
    >>> list(render_string(tmpl.encode('utf-8'), flags=returns_iter))
    ['\u3053\u3093\u306b\u3061\u306f']

    Bytes-in, bytes-iterator-out:
    >>> list(render_string(tmpl.encode('utf-8'),
    ...                    flags=returns_bytes | returns_iter))
    [b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf']


    >>> renderer = render_string(tmpl, flags=returns_renderer)
    >>> renderer # doctest: +ELLIPSIS
    <__main__.Template object ...>
    >>> frame = {}
    >>> bool(frame)
    False
    >>> renderer(frame) # The first argument is frame (namespace),
    ...                 # this will be changed inplace.
    '\u3053\u3093\u306b\u3061\u306f'
    >>> bool(frame)
    True
    """
    cachekey = 'string', string_or_bytes
    try:
        template = cache[cachekey]
    except LookupError:
        if isinstance(string_or_bytes, StringType):
            string_or_bytes = io.StringIO(string_or_bytes)
        elif isinstance(string_or_bytes, BytesType):
            string_or_bytes = io.BytesIO(string_or_bytes)
        else:
            raise TypeError(string_or_bytes)

        template = Template(string_or_bytes)
        if cachekey:
            cache[cachekey] = template

    if flags & returns_renderer:
        assert not locals
        return template

    return template(makedict(default_context, locals), flags)


def render_resource(package_or_requirement, resource_name, locals={}, flags=0):
    r"""Render a package resource via `pkg_resources.resource_stream()`.
    """
    import pkg_resources

    cachekey = 'resource', package_or_requirement, resource_name
    try:
        template = cache[cachekey]
    except LookupError:
        template = Template(
            pkg_resources.resource_stream(package_or_requirement, resource_name))
        if cachekey:
            cache[cachekey] = template

    if flags & returns_renderer:
        assert not locals
        return template

    return template(makedict(default_context, locals), flags)


if __name__ == '__main__':
    # register: setup.py check sdist register upload
    # upload: setup.py check sdist upload
    import __main__
    import os
    import doctest
    import distutils.core

    __main__.__name__ = os.path.splitext(os.path.basename(__file__))[0]
    target = __main__

    if 'check' in sys.argv:
        doctest.testmod(target)
        try:
            import docutils.core
        except ImportError:
            pass
        else:
            s = docutils.core.publish_string(target.__doc__, writer_name='html')
            with open(os.path.splitext(__file__)[0] + '.html', 'wb') as fp:
                fp.write(s)

    # http://docs.python.org/3/distutils/apiref.html?highlight=setup#distutils.core.setup
    distutils.core.setup(
        name=target.__name__,
        version=target.__version__,
        description=target.__doc__.splitlines()[0],
        long_description=target.__doc__,
        author=target.__author__,
        author_email=target.__author_email__,
        url=target.__url__,
        classifiers=target.__classifiers__,
        license=target.__license__,
        py_modules=[target.__name__, ],
        )


