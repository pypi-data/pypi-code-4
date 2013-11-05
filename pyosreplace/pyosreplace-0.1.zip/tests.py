#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import osreplace
import tempfile
import unittest
import shutil


class TestOSReplace(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_osreplace_ascii(self):
        f1 = os.path.join(self.tempdir, "f1")
        f2 = os.path.join(self.tempdir, "f2")
        self.osreplace_replace(f1, f2)

    def test_osreplace_unicode(self):
        f1 = os.path.join(self.tempdir, b"b\xc3\xa4".decode("utf-8"))
        f2 = os.path.join(self.tempdir, b"b\xc3\xb6".decode("utf-8"))
        self.osreplace_replace(f1, f2)

    def osreplace_replace(self, f1, f2):
        with open(f1, "w") as f:
            f.write("f1")
        with open(f2, "w") as f:
            f.write("f2")

        osreplace.replace(f1, f2)
        self.assertFalse(os.path.isfile(f1))
        self.assertTrue(os.path.isfile(f2))
        with open(f2) as f:
            self.assertEqual(f.read(), "f1")

        osreplace.replace(f2, f1)
        self.assertTrue(os.path.isfile(f1))
        self.assertFalse(os.path.isfile(f2))
        with open(f1) as f:
            self.assertEqual(f.read(), "f1")


def test_main():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestOSReplace))
    return suite

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(test_main())
    sys.exit(not result.wasSuccessful())
