# -*- coding: utf-8 -*-

"""Pygments lexer for PVS source files
"""

from pygments.lexer import Lexer, LexerContext, RegexLexer, ExtendedRegexLexer, \
    bygroups, include, using, this, do_insertions
from pygments.token import Punctuation, Text, Comment, Keyword, Name, String, \
    Generic, Operator, Number, Whitespace, Literal

class PVSLexer(RegexLexer):
    """
    Lexer for the prototype verification system `PVS
    <http://pvs.csl.sri.com>`_ language.
    """

    name = 'PVS'
    aliases = ['pvs']
    filenames = ['*.pvs']
    mimetypes = ['text/x-pvs']

    # Optional comment or whitespace
    ws = r'(?:(?:\s|%.*\n)*)'

    namespace_kw = [
        'THEORY', 'DATATYPE', 'CODATATYPE', 'BEGIN', 'END', 'SUBTYPES',
        'WITH(?=' + ws + 'SUBTYPES)', 'LIBRARY',
    ]

    var_kw = [
        'VAR',
    ] 

    type_kw = [
        'TYPE', 'NONEMPTY_TYPE', 'TYPE+', 'FROM',
    ]

    formula_kw = [
        'AXIOM', 'CHALLENGE', 'CLAIM', 'CONJECTURE', 'COROLARRY', 'FACT',
        'FORMULA', 'LEMMA', 'OBLIGATION', 'POSTULATE', 'PROPOSITION',
        'SUBLEMMA', 'THEOREM', 'ASSUMPTION', 'JUDGEMENT',
    ]

    keywords = [
        'ASSUMING', 'ENDASSUMING', 'IF', 'THEN', 'ELSE', 'ELSIF', 'ENDIF',
        'CASES', 'OF', 'ENDCASES', 'COND', 'ENDCOND', 'TABLE', 'ENDTABLE',
        'LET', 'FORALL', 'EXISTS', 'LAMBDA', 'EXPORTING', 'ALL', 'BUT',
        'CLOSURE', 'IMPORTING', 'WHERE', 'IN', 'CONTAINING',
        'WITH', 'MEASURE', 'CONVERSION', 'CONVERSION+',
        'CONVERSION-', 'AUTO_REWRITE', 'AUTO_REWRITE+', 'AUTO_REWRITE-',
        'HAS_TYPE', 'SUBTYPE_OF', 'FUNCTION', 'ARRAY', 'RECURSIVE', 'MACRO',
        'INDUCTIVE', 'CORECURSIVE', 'COINDUCTIVE',
    ]

    word_operators = [
        'IFF', 'IMPLIES', 'WHEN', 'OR', 'XOR', 'AND', 'ANDTHEN', 'ORELSE',
        'NOT', 'O',
    ]

    operators = '[\-\+\*/:=\|><\.&^~#@!\]\[(){}]'
    uoperators = [   
        u'〈', u'〉',
        u'〚', u'〛', u'«', u'»', u'《', u'》', u'⌈', u'⌉', u'⌊', u'⌋', u'⌜', u'⌝', u'⌞', u'⌟',
        u'□', u'◇', u'¬', u'◯', u'√',
        u'∘', u'∨', u'∧', u'⊕', u'⊘', u'⊗', u'⊖', u'⊙', u'⊛', u'⨁', u'⨂', u'⨀',
        u'⊢', u'⊨', u'±', u'∓', u'∔', u'×', u'÷', u'⊞', u'⊟', u'⊠', u'≁', u'∼', u'≃', u'≅', u'≇',
        u'≈', u'≉', u'≍', u'≎', u'≏', u'≐', u'≗', u'≙', u'≡', u'⋈', u'≤', u'≥', u'≦', u'≧',
        u'≨', u'≩', u'≪', u'≫', u'≮', u'≯', u'≰', u'≱', u'≺', u'≻', u'◁', u'▷',
        u'∈', u'∉', u'∋', u'∩', u'∪', u'⊂', u'⊃', u'⊄', u'⊅', u'⊆', u'⊇', u'⊎', u'⊊', u'⊋',
        u'⊏', u'⊐', u'⊓', u'⊔', u'⋀', u'⋁', u'⋂', u'⋃', u'•', u'←', u'↑', u'→', u'↓', u'↝', u'↦',
        u'⇐', u'⇒', u'⇑', u'⇓', u'⇔', u'∇', u'⊣', u'⊥', u'⊩', u'◯', u'★', u'✠', u'≠',
    ]

    constants = [
        'TRUE', 'FALSE', 'PROJ_\d+', 'IN_\d+\??', 'OUT_\d+',
    ]

    ident = '[a-zA-Z0-9_?]+'

    tokens = {
        'whitespace': [
            (r'\s+', Text),
            (r'%.*', Comment.Single),
        ],
        'root': [
            include('whitespace'),
            (r'(?i)\b(%s)\b' % '|'.join(namespace_kw), Keyword.Namespace),
            (r'(?i)\b(%s)\b' % '|'.join(type_kw + formula_kw), Keyword.Type),
            (r'(?i)\b(%s)\b' % '|'.join(var_kw), Keyword.Declaration),
            (r'(?i)\b(%s)\b' % '|'.join(constants), Name.Constant),
            (r'(?i)\b(%s)\b' % '|'.join(keywords), Keyword),
            (r'`\d+', Keyword),
            (r'\d+', Number.Integer),
            (r'(?i)\b(%s)\b' % '|'.join(word_operators), Operator.Word),
            (operators, Operator),
            (r'[%s]' % ''.join(uoperators), Operator),
            (r'->|[:,`;§]|[\[(]#?|#?[\])]|[({]:?|:?[})]|[({\[]\||\|[)}\]]|{{|}}|\|', Punctuation),
            (r'"', String.Double, 'string'),
            (r'\b' + ident + r'(?=' + ws + '\.)', Name.Namespace),
            (r'\b' + ident, Name),
        ],
        'string': [
            (r'[^"]+', String.Double),
            (r'"', String.Double, '#pop'),
        ],
    }

    def analyse_text(text):
        up = text.upper()
        return up.find('THEORY') != -1 or up.find('DATATYPE') != -1
