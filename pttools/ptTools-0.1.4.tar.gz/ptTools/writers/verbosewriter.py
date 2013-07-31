#!/usr/bin/env python3

"""Module providing a VerboseParseTreeWriter for printing
ptTools.ParseTreeNode as originally formatted to an output channel."""

__all__ = [
    'VerboseParseTreeWriter',
    ]

from . abstractwriter import AbstractParseTreeWriter


class VerboseParseTreeWriter(AbstractParseTreeWriter):

    """Writer for printing ptTools.ParseTreeNodes as originally
    formatted to output channel."""

    def _write_continuation(self, tok):
        """Writes soft linebreak."""
        self._write_str(tok.predecessor.rest)

    def _write_indent(self, tok):
        """Writes appropriate leading spaces, preceeding a given
        token."""
        self._write_space(tok.length)    

    def _write_space(self, i):
        """Writes n spaces."""
        assert(i >= 0)
        if i:
            self._write_str(' ' * i)

    def _write_spacing(self, tok):
        """Writes appropriate leading spaces, preceeding a given
        token."""
        self._write_space(tok.leading_space)

    def _write_token(self, tok):
        """Writes token to self.out."""
        if tok.isindent():
            self._write_indent(tok)
        else:
            if tok.iscontinuation():
                self._write_continuation(tok)
            self._write_spacing(tok)
            self._write(tok)

    def write_newline(self, count=1):
        """Writes '\\n' to self.out.  Takes optional number for the
        amount of newlines to write."""
        self._write_str('\n' * count)

