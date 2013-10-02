from __future__ import print_function
from __future__ import unicode_literals

from lib2to3.fixer_util import FromImport, Name, Newline
from lib2to3.pytree import Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token


__version__ = '0.3.2'


def check_future_import(node):
    """If this is a future import, return set of symbols that are imported,
    else return None."""
    # node should be the import statement here
    if not (node.type == syms.simple_stmt and node.children):
        return set()
    node = node.children[0]
    # now node is the import_from node
    if not (node.type == syms.import_from and
            node.children[1].type == token.NAME and
            node.children[1].value == '__future__'):
        return set()
    node = node.children[3]
    # now node is the import_as_name[s]
    if node.type == syms.import_as_names:
        result = set()
        for n in node.children:
            if n.type == token.NAME:
                result.add(n.value)
            elif n.type == syms.import_as_name:
                n = n.children[0]
                assert n.type == token.NAME
                result.add(n.value)
        return result
    elif node.type == syms.import_as_name:
        node = node.children[0]
        assert node.type == token.NAME
        return set([node.value])
    elif node.type == token.NAME:
        return set([node.value])
    else:
        assert 0, 'strange import'


def add_future_import(tree, name):
    """Add future import.

    From: https://github.com/facebook/tornado

    Copyright 2009 Facebook

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.

    """
    if not isinstance(tree, Node):
        # Empty files (usually __init__.py) show up as a single Leaf
        # instead of a Node, so leave them alone
        return

    first_stmt = tree.children[0]
    if is_docstring(first_stmt):
        # Skip a line and add the import after the docstring
        tree.insert_child(1, Newline())
        pos = 2
    elif first_stmt.prefix:
        # No docstring, but an initial comment (perhaps a #! line).
        # Transfer the initial comment to a new blank line.
        newline = Newline()
        newline.prefix = first_stmt.prefix
        first_stmt.prefix = ''
        tree.insert_child(0, newline)
        pos = 1
    else:
        # No comments or docstring, just insert at the start
        pos = 0
    tree.insert_child(
        pos,
        FromImport('__future__', [Name(name, prefix=' ')]))
    tree.insert_child(pos + 1, Newline())  # terminates the import stmt


# copied from fix_tuple_params.py
def is_docstring(stmt):
    return isinstance(stmt, Node) and \
        stmt.children[0].type == token.STRING
