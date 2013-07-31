#!/usr/bin/env python3

"""Module Providing abstract superclass for writing trees to output
channels."""

__all__ = [
    'AbstractParseTreeWriter',
    'AbstractTreeWriter',
    ]


class AbstractTreeWriter(object):

    """Abstract superclass to writers, writing trees to a channel.

    Trees must be of the following form:
    
        node ::= ( INT (', 'node | ', 'STR)+ )        

        (The inner parenthesis belong to the rule description).

    AbstractTreeWriter is initialized with an output channel.
    When applied to a tree node by calling self.write_node(node),
    that node is traversed preorder.  Style attributes and contents
    are retrieved from each node on the branch, and output to self.out
    during traversal.

    For writing a node (leaves only), self._write_leaf(node) is called.

    self._get_node_style(node) may be implemented by subclasses to
    retrieve style information from a node.  The identical style
    object is then passed to self._write_opening_markup(style_obj), as
    well as to self._write_closing_markup(style_obj).  Those methods
    are called for inner nodes as well as for leaves, before entering
    and after leaving a node.

    All output is finally passed to self._write(str).

    """

    def __init__(self, out):
        """Initialized with a channel."""
        self.out = out
        """The output channel."""
    
    def _get_node_style(self, node):
        """Returns style description of node.  Defaults to None.

        This method may be reimplemented by subclasses to retrieve and
        process a node's attributes.  The return value is passed to
        self._write_opening_markup() and self._write_closing_markup(),
        respectively.
        
        """
        return None

    def _write(self, obj):
        """Writes obj to self.out."""
        self._write_str(str(obj))

    def _write_closing_markup(self, style):
        """Does nothing.  Subclass responsibility."""
        pass

    def _write_opening_markup(self, style):
        """Does nothing.  Subclass responsibility."""
        pass

    def _write_leaf(self, node):
        """Writes node.__str__() to self.out."""
        self._write(node)

    def write_node(self, node):
        """Writes node with children to self.out."""
        style = self._get_node_style(node)
        self._write_opening_markup(style)
        if isinstance(node, tuple):
            for child in node[1:]:
                self.write_node(child)
        else:
            self._write_leaf(node)
        self._write_closing_markup(style)                

    def _write_str(self, string):
        """Writes string to self.out."""
        self.out.write(string)


class AbstractParseTreeWriter(AbstractTreeWriter):

    """Abstract superclass for writers that use the ptTools.parsetree
    datamodell.

    In addition to ._get_node_style, self._get_token_style(token) may
    be implemented by subclasses to retrieve style information from
    tokens.  As in ._get_node_style, the retrieved style object is
    passed to ._write_opening_markup, and to ._write_closing_markup.

    """

    def _get_token_style(self, tok):
        """Returns style description of token.  Defaults to None.

        This method may be reimplemented by subclasses to retrieve and
        process a token's attributes.  The return value is passed to
        self._write_opening_markup() and self._write_closing_markup(),
        respectively.
        
        """
        return None

    def _write_leaf(self, node):
        """Writes all tokens of a terminal node."""
        for tok in node.tokens:
            self._write_token(tok)

    def _write_token(self, tok):
        """Writes token to self.out, applying opening and closing
        markups."""
        style = self._get_token_style(tok)
        self._write_opening_markup(style)
        self._write(tok)
        self._write_closing_markup(style)                        
