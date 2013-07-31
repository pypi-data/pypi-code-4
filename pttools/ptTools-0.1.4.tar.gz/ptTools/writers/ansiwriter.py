#!/usr/bin/env python3

"""Module providing an AnsiParseTreeWriter for formatted printing of
ptTools.ParseTreeNodes to an output channel on linux systems."""

__all__ = [
    'BLINK',
    'BOLD',
    'COLOR',
    'COLORS',
    'COMMENT',
    'PRECEDENCE',
    'UNDERLINE',
    'AnsiParseTreeWriter',
    ]

from . verbosewriter import VerboseParseTreeWriter


BLINK = 'blink'
BOLD = 'bold'
COLOR = 'color'
COLORS = 'colors'
COMMENT = 'comment'
PRECEDENCE = 'precedence'
UNDERLINE = 'underline'


class AnsiParseTreeWriter(VerboseParseTreeWriter):

    """Writer for printing attributed ptTools.ParseTreeNodes to an
    output channel on linux systems.

    Note that the ansi markup sequence behaves differently from
    e.g. html.  A closing markup closes all opened markups.  However,
    opening sequences CAN be nested, but are all closed when
    encountering the closing sequence.

    The current style description is updated while traversing
    non-terminal nodes, but not written until reaching a terminal.
    
    Every token is embraced in its own opening and closing markup
    sequence.

    """

    ## ANSI print sequence:
    ## {ESC}[{ATTR};{BG};{256colors};{FG}m
    ## e.g.: "\033[38;5;255mfoobar\033[39m"

    _ansi_constants = {'ESC': '\033',
                       'BG': '5',
                       'FG': '0',}

    def __init__(self, out):
        """Initialized with an output channel."""
        super().__init__(out)
        self._style = {}
        """The currently queued style dictionary."""
        
    def _ansi_dict_from(self, style):
        """Converts style dictionary to ansi description dictionary."""
        ## Order of attributest IS significant!
        attr = '38'
        if style.get(BLINK):
            attr = '5;' + attr            
        if style.get(UNDERLINE):
            attr = '4;' + attr
        if style.get(BOLD):
            attr = '1;' + attr
        ansidict = {'ATTR': attr,
                    'CLR' : style.get(COLOR,'')}
        ansidict.update(self._ansi_constants)
        return ansidict

    def _get_node_style(self, node):
        """Retrieves all inherited attributes of node and merges them
        to one style dictionary.

        Called from super.write_node(node).

        """
        return node.all_attributes
        
    def _get_token_style(self, tok):
        """Retrieves all attributes of token and returns style
        dictionary.

        Called from super.write_token(token).

        """
        return tok.attributes

    def _write_closing_markup(self, style=None):
        """Writes ansi style closing sequence to self.out, and clears
        queued style information."""
        self._write_closing_markup_raw(self._style)
        self._style = {}

    def _write_closing_markup_raw(self, style):
        """Writes ansi style closing sequence to self.out without
        altering the queued style description."""
        if style:
            self._write_str("{ESC}[{FG}m".format(**self._ansi_constants))

    def _write_leaf(self, node):
        """Writes terminal node with its tokens."""
        if not node.tokens:
            return
        else:
            ## Tokens except the last token in terminalnode.tokens
            ## define their markup themselves, whereas the last token
            ## receives its node's markups.
            for tok in node.tokens[:-1]:
                token_style = self._get_token_style(tok)
                self._write_opening_markup_raw(token_style)
                super()._write_token(tok)
                self._write_closing_markup_raw(token_style)
            self._write_token(node.token) ## (last token).

    def _write_opening_markup(self, style):
        """Queues style dictionary for output.

        This method reimplements its superclass method.  Called for
        each node with the intention to write opening markups to
        self.out.  Here, we only queue the style information as we may
        have to insert tokens with different markups, before.
        
        """
        if style:
            self._style.update(style)

    def _write_opening_markup_raw(self, style):        
        """Writes opening sequence as described by ansi_dict to
        self.out, without altering the queued style description."""
        if style:
            ansi_dict = self._ansi_dict_from(style)
            self._write_str('{ESC}[{ATTR};{BG};{CLR}m'.format(**ansi_dict))

    def _write_indent(self, tok):
        """Calls super.

        TODO - Suspend markup (to avoid preceeding underlines in
        multiline comments.).

        """
        super()._write_indent(tok)

    def _write_spacing(self, tok):
        """Calls super.

        TODO - Suspend markup (to avoid preceeding underlines in
        multiline comments.).

        """
        super()._write_spacing(tok)

    def _write_token(self, tok):
        """Writes token and markups to self.out."""
        self._write_opening_markup_raw(self._style)
        super()._write_token(tok)
        self._write_closing_markup_raw(self._style)
        
