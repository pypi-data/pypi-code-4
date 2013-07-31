#!/usr/bin/env python3

"""Wrapper package for tokenize.

ptTools.tokenizer wraps the tokenize package to provide a LinkedToken
class, and a generator for its instances.

LinkedToken is a subclass of tokenize.TokenInfo.

ptTools.tokenizer.generate_tokens returns an iterator similar to the
tokenize.generate_tokens generator function, but yielding LinkedToken
instances instead of TokenInfo instances.

"""

__author__ = "Markus Rother - python@markusrother.de"
__date__ = "06/2013"
__version__ = "0.1"

__all__ = [
    'generate_tokens',
    'identify',
    'SYMBOLS',
    'LinkedToken',
    'Tokenizer',
    ]

from . tokenizer import generate_tokens
from . tokenizer import SYMBOLS
from . tokenizer import identify
from . tokenizer import Tokenizer
from . linkedtoken import LinkedToken
