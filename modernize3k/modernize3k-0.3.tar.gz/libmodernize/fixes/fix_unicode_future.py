from __future__ import absolute_import
from __future__ import unicode_literals

from lib2to3.fixes import fix_unicode

from libmodernize import add_future_import, check_future_import


class FixUnicodeFuture(fix_unicode.FixUnicode):

    def start_tree(self, tree, filename):
        self.found_unicode = False

    def transform(self, node, results):
        res = super(FixUnicodeFuture, self).transform(node, results)
        if res:
            self.found_unicode = True
        return res

    def finish_tree(self, tree, name):
        super(FixUnicodeFuture, self).finish_tree(tree, name)

        if not self.found_unicode:
            return

        for node in tree.children:
            if 'unicode_literals' in check_future_import(node):
                return

        add_future_import(tree, 'unicode_literals')
