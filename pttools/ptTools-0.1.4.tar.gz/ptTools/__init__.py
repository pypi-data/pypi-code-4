#!/usr/bin/env python3
# The following comment is used to auto-create the README.txt file.
"""The ptTools packages provides a domain specific language, for
pattern matching on trees - python parsetrees in particular.

Matching parsetree nodes instead of regular expression based string
search, allows fine-grained, semantic control over search results.
The second major benefit is that the matches are instantiated
parsetree nodes, that can be manipulated and recompiled.  Parsetree
based search is of interest especially when manipulating or
substituting selected nodes, e.g. for testing, or code analysis.

The domain specific language of ptTools patterns consists of a family
of pattern objects, all of which can be expressed in valid python
code.  Binary and unary operators similar to those of regular
expressions are available. The resulting pattern language resembles
the grammar rules it matches.

Emphasis was put on an intuitive interface, and a clean and easily
extensible object-oriented design.  The components are loosely
coupled.  For example the pattern objects can be matched against
tuples as well as against attributed parsetree nodes.  The parsetree
nodes may or may not hold references to tokens, which again may or may
not be attributed.

"""

__author__  = "Markus Rother - python@markusrother.de"
__date__    = "06/2013"
__version__ = "0.1"

__all__ = [
    'parsetree',
    'ptpatterns',
    'tokenizer',
    'writers',
    ]

from . import tokenizer
from . import parsetree
from . import writers
from . import ptpatterns

from . doc import _mkreadme
