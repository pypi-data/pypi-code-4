import re
from functools import reduce

JOIN_PAGEBREAK = '\\pagebreak{}'
JOIN_NEWPAGE = '\\newpage{}'
JOIN_CLEARPAGE = '\\clearpage{}'
JOIN_CLEARDOUBLEPAGE = '\\cleardoublepage{}'

#===============================================================================
# LaTeX escaping
#===============================================================================
LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)

def escape_tex(text):
    '''Escape the given `text` to safe LaTeX'''

    newval = text
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

#===============================================================================
# Environments
#===============================================================================
def env_partition(st, env):
    r"""Similar to str.partition, but rather than using a given separator,
    it partition the string across some LaTeX environment.
    
    >>> tex = r'''some text
    ... \begin{foo}
    ...   foo env
    ... \end{foo}
    ... ham!'''
    >>> pre, env, post = env_partition(tex, 'foo')
    >>> print(env)
    \begin{foo}
      foo env
    \end{foo}
    >>> pre + post
    'some text\n\nham!'
    """
    pre, begin, post = st.partition('\\begin{%s}' % env)
    envdata, end, post = post.partition('\\end{%s}' % env)
    return (pre, begin + envdata + end, post)

def env_content(env_data):
    r'''Returns a tuple with (content, args) for a given environment block.
    
    >>> tex = r"\begin{foo}[ham]{spam} foo content \end{foo}"
    >>> env_content(tex)
    ('foo content', ['ham', 'spam'])
    '''
    _, __, content = env_data.partition('}')
    content, _, __ = content.rpartition('\\end')
    args = []

    # Check for optional arguments
    if content.startswith('['):
        arg, _, content = content[1:].partition(']')
        args.append(arg)

    # Read all arguments
    while content.startswith('{'):
        arg, _, content = content[1:].partition('}')
        args.append(arg)

    return (content.strip(), args)

#===============================================================================
# File reading
#===============================================================================
def readfile(source, path=None):
    '''Return a tuple (data, path) with the data and path name for the input 
    file or string.'''

    if isinstance(source, str):
        if path is None:
            path = '<string>'
        return source, path
    else:
        data = source.read()
        path = getattr(source, 'name', path)
        return (data, path)

#===============================================================================
# Document manipulation
#===============================================================================
def join_tex(docs, join='\n', as_document=True):
    r'''Aggregate the different versions of the given source into a single 
    document.
    
    Parameters
    ----------
    
    join : str
        A string used to join different alternatives. One can also use the 
        constants JOIN_CLEARPAGE, JOIN_CLEARDOUBLEPAGE, JOIN_NEWPAGE, and 
        JOIN_PAGEBREAK for the corresponding LaTeX constructs.
    as_document : bool
        If True (default), joins the content inside \begin{document} and
        \end{document} and use a common preamble for the output document.
    
    Example
    -------
    
    It can join the different sections in a straightforward manner
    
    >>> alt = AltSource(r'foo bar \ALT{ham | spam | eggs}')
    >>> print(join_tex(as_document=False))
    foo bar ham
    foo bar spam
    foo bar eggs
    
    Most LaTeX documents, however, are divided into "preamble" and "document"
    parts. In this case, we want to join the document parts and use a common
    preamble.
    
    >>> txt = r"""\documentclass{article}
    ... \begin{document}
    ... foo: \ALT{ham | spam | eggs}
    ... bar: \ALT{0|1|2}
    ... \end{document}""" 
    >>> print(AltSource(txt).aggregate(join=JOIN_CLEARPAGE))
    \documentclass{article}
    \begin{document}
    foo: ham
    bar: 0
    \clearpage{}
    foo: spam
    bar: 1
    \clearpage{}
    foo: eggs
    bar: 2
    \end{document}
    '''
    if not as_document:
        return '\n'.join(docs)
    else:
        docs = [split_preamble(doc) for doc in docs]
        preamble = docs[0][0]
        if any(preamble != p for (p, d) in docs):
            raise ValueError('preambles are not identical')
        body = join.join(d for (p, d) in docs)
        return '%s\\begin{document}%s\\end{document}' % (preamble, body)

def split_preamble(doc):
    '''Splits a LaTeX document into a tuple (preamble, document)'''

    preamble, _, document = doc.partition(r'\begin{document}')
    document, _, __ = document.partition(r'\end{document}')
    return preamble, document

#===============================================================================
# Math functions
#     from: https://gist.github.com/endolith/114336
#===============================================================================
from fractions import gcd as _gcd
def gcd(numbers):
    """Return the greatest common divisor of the given integers"""
    return reduce(_gcd, numbers)

def lcm(numbers):
    """Return lowest common multiple."""
    def lcm(a, b):
        return (a * b) // gcd([a, b])
    return reduce(lcm, numbers, 1)

#===============================================================================
# Iterators
#===============================================================================
class bufferediter(object):
    """Buffered iterator. Items can be pushed to the main iteration."""

    def __init__(self, obj):
        self._iter = iter(obj)
        self._buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer:
            return self._buffer.pop()
        return next(self._iter)

    def push(self, value):
        '''Add a single value to buffer'''
        self._buffer.append(value)

    def push_many(self, values):
        '''Add a sequence of values to buffer'''
        self._buffer.extend(values)


