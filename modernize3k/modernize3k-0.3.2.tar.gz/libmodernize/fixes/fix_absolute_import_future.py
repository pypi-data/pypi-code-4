"""Like lib2to3.fixes.fix_import, but add the absolute_import future to all
files that contain imports."""

from __future__ import absolute_import

from lib2to3.fixes import fix_import
from lib2to3.pygram import python_symbols
from lib2to3.pgen2 import token

from libmodernize import add_future_import, check_future_import


class FixAbsoluteImportFuture(fix_import.FixImport):

    def finish_tree(self, tree, name):
        super(FixAbsoluteImportFuture, self).finish_tree(tree, name)

        for node in tree.children:
            if 'absolute_import' in check_future_import(node):
                return

            if not (node.type == python_symbols.simple_stmt and node.children):
                continue

            # Only add future import if there exists imports in the file.
            # Otherwise we end up with a lot of useless clutter.
            node = node.children[0]
            if (
                node.type == python_symbols.import_name or
                (node.type == python_symbols.import_from and
                 node.children[1].type == token.NAME and
                 node.children[1].value != '__future__')
            ):
                add_future_import(tree, 'absolute_import')
                return
