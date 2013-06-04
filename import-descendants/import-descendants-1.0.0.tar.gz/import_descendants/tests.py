# -*- coding: utf-8 -*-
# (c) 2013 Bright Interactive Limited. All rights reserved.
# http://www.bright-interactive.com | info@bright-interactive.com

"""
Tests for import_descendants.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_child_file_imported(self):
        from import_descendants.test_example import CONSTANT_IN_CHILD_FILE
        self.assertEqual('in child file', CONSTANT_IN_CHILD_FILE)

    def test_child_dir_imported(self):
        from import_descendants.test_example import CONSTANT_IN_CHILD_DIR
        self.assertEqual('in child dir', CONSTANT_IN_CHILD_DIR)

    def test_grandchild_file_imported(self):
        from import_descendants.test_example import CONSTANT_IN_GRANDCHILD_FILE
        self.assertEqual('in grandchild file', CONSTANT_IN_GRANDCHILD_FILE)

    def test_grandchild_dir_imported(self):
        from import_descendants.test_example import CONSTANT_IN_GRANDCHILD_DIR
        self.assertEqual('in grandchild dir', CONSTANT_IN_GRANDCHILD_DIR)
